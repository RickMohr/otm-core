from math import sqrt

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection

from treemap.instance import Instance
from treemap.models import MapFeature


class Command(BaseCommand):
    args = '<instance_url_name, [grid_size_pixels]>'
    help = 'Sets hideAtZoom for all map features in an instance'

    def handle(self, *args, **options):
        if len(args) < 1:
            raise CommandError('Please specify an instance URL name')

        try:
            url_name = args[0]
            instance = Instance.objects.get(url_name=url_name)
        except ObjectDoesNotExist:
            raise CommandError('Instance "%s" not found' % url_name)

        if len(args) > 2:
            raise CommandError('Command takes 1 or 2 arguments')

        if len(args) == 1:
            grid_pixels = 1.77
        else:
            try:
                grid_pixels = float(args[1])
            except ValueError:
                raise CommandError('Second argument must be a number')

        self.stdout.write(
            'Clearing hide_at_zoom for all map features in this instance')
        MapFeature.objects.all() \
            .filter(instance=instance) \
            .update(hide_at_zoom=None)

        # for zoom in range(6, 5, -1):
        for zoom in range(14, 5, -1):
            sql = make_sql(instance, zoom, grid_pixels)
            with connection.cursor() as cursor:
                cursor.execute(sql)
            print_summary(instance, grid_pixels, zoom)


def print_summary(instance, grid_pixels, zoom):
    #n = MapFeature.objects.filter(instance=instance).count()
    grid_size_wm = get_grid_size_wm(grid_pixels, zoom)
    features = MapFeature.objects.filter(instance=instance, hide_at_zoom=None)
    snapped_features = features.snap_to_grid(grid_size_wm)
    nvis = features.count()
    print('%s  %s' % (zoom, nvis))
    if nvis < 3:
        print("    grid_size_wm = %s" % grid_size_wm)
        for i in range(0, nvis):
            feature = features[i]
            snapped = snapped_features[i]
            print("    %s: (%s, %s) (%s, %s)" % (
                feature.id, feature.geom.x, feature.geom.y, snapped.snap_to_grid.x, snapped.snap_to_grid.y))


def make_sql(instance, zoom, grid_pixels):
    grid_size_wm = get_grid_size_wm(grid_pixels, zoom)
    #print(grid_size_wm)

    sql = """
        WITH featuresToHide AS (
            WITH mapfeature AS (
                 SELECT f.id, f.the_geom_webmercator
                 FROM treemap_mapfeature f
                 INNER JOIN treemap_instance i ON f.instance_id=i.id
                 WHERE i.id=%s AND f.hide_at_zoom IS NULL
            )
            SELECT mapfeature.id FROM mapfeature
            LEFT OUTER JOIN
                (SELECT DISTINCT ON (geom) id, ST_SnapToGrid(the_geom_webmercator, %s) AS geom
                    FROM mapfeature
                ) AS distinctRows
                ON mapfeature.id = distinctRows.id
            WHERE distinctRows.id IS NULL
        )
        UPDATE treemap_mapfeature f
        SET hide_at_zoom = %s
        FROM featuresToHide
        WHERE f.id = featuresToHide.id;
        """ % (instance.id, grid_size_wm, zoom)

    return sql


def get_grid_size_wm(grid_pixels, zoom):
    wm_world_width = 40075016.6856
    tile_size = 256
    wm_units_per_pixel = wm_world_width / (tile_size * pow(2, zoom))
    grid_size_wm = grid_pixels * wm_units_per_pixel
    return grid_size_wm



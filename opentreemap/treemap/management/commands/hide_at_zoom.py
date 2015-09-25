from math import sqrt
from django.contrib.gis.geos import Point

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
        clear_hide_at_zoom(instance)

        compare(instance, grid_pixels, 14, 11)


def compare(instance, grid_pixels, max_zoom, min_zoom):
    # allow comparing sets of Point objects
    Point.__repr__ = lambda self: '(%s, %s)' % (self.x, self.y)
    Point.__hash__ = lambda self: hash(self.__repr__())

    features_by_zoom = hide(instance, grid_pixels, max_zoom, min_zoom)
    counts = [len(features) for features in features_by_zoom]
    print("0: %s" % counts)
    while True:
        clear_hide_at_zoom(instance)
        features_by_zoom2 = hide(instance, grid_pixels, max_zoom, min_zoom)
        counts2 = [len(features) for features in features_by_zoom2]
        if counts2 == counts:
            print('Match')
        else:
            print("%s" % counts2)
            for i in range(0, len(counts)):
                features2 = features_by_zoom2[i]
                if counts2[i] != counts[i]:
                    features = features_by_zoom[i]
                    snaps = set(features)
                    snaps2 = set(features2)
                    diff = snaps2 - snaps if len(snaps2) > len(snaps) else snaps - snaps2
                    print(diff)
                    return


def clear_hide_at_zoom(instance):
    MapFeature.objects.all() \
        .filter(instance=instance) \
        .update(hide_at_zoom=None)

def get_snapped_features(features, grid_size_wm):
    snapped = features.snap_to_grid(grid_size_wm).values_list('snap_to_grid', flat=True)
    l = list(snapped)
    s = set(snapped)
    if len(l) != len(s):
        print('Mismatch: n1=%s n2=%s' % (len(l), len(s)))
    return list(snapped)


def hide(instance, grid_pixels, max_zoom, min_zoom):
    features_by_zoom = []
    # for zoom in range(6, 5, -1):
    # for zoom in range(14, 5, -1):
    # for zoom in range(11, 10, -1):
    for zoom in range(max_zoom, min_zoom - 1, -1):
        grid_size_wm = get_grid_size_wm(grid_pixels, zoom)
        sql = make_sql(instance, zoom, grid_pixels)
        with connection.cursor() as cursor:
            cursor.execute(sql)
        #print_summary(instance, grid_pixels, zoom)
        qs = MapFeature.objects.filter(instance=instance, hide_at_zoom=None)
        snaps = get_snapped_features(qs, grid_size_wm)
        features_by_zoom.append(snaps)
    return features_by_zoom


def print_summary(instance, grid_pixels, zoom):
    #n = MapFeature.objects.filter(instance=instance).count()
    grid_size_wm = get_grid_size_wm(grid_pixels, zoom)
    features = MapFeature.objects \
        .filter(instance=instance, hide_at_zoom=None) \
        .snap_to_grid(grid_size_wm)
    nvis = features.count()
    print('%s  %s' % (zoom, nvis))
    if nvis < 3:
        print("    grid_size_wm = %s" % grid_size_wm)
        for feature in features:
            x = feature.snap_to_grid.x / grid_size_wm
            y = feature.snap_to_grid.y / grid_size_wm
            print("    %s: (%s, %s) (%s, %s)" % (
                feature.id,
                feature.snap_to_grid.x, feature.snap_to_grid.y,
                x, y))


def verify(instance, grid_size_wm):
    features = MapFeature.objects.filter(instance=instance, hide_at_zoom=None)
    n1 = features.count()
    snapped = get_snapped_features(features, grid_size_wm)
    n2 = len(set(snapped))
    if n1 != n2:
        print('Mismatch: n1=%s n2=%s' % (n1, n2))
    else:
        print('verified')


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


def get_grid_size_wm_int(grid_pixels, zoom):
    wm_world_width = 40075016.6856
    tile_size = 256
    wm_units_per_pixel_zoom_14 = wm_world_width / (tile_size * pow(2, 14))
    grid_size_wm_zoom_14 = round(grid_pixels * wm_units_per_pixel_zoom_14)
    grid_size_wm = grid_size_wm_zoom_14 * pow(2, 14 - zoom)
    return grid_size_wm


def get_grid_size_wm(grid_pixels, zoom):
    wm_world_width = 40075016.6856
    tile_size = 256
    wm_units_per_pixel = wm_world_width / (tile_size * pow(2, zoom))
    grid_size_wm = grid_pixels * wm_units_per_pixel
    return grid_size_wm



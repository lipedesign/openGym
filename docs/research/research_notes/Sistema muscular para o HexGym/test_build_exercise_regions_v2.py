#!/usr/bin/env python3
"""Testes das regras da v2 do mapa de exercícios (python3 -m unittest test_build_exercise_regions_v2).

Lê só o texto do catálogo, como o gerador. Cada caso é um exercício real pelo id.
"""
import json
import unittest

import build_exercise_regions as B

B.use_v2()
ROWS, _, _ = B.build()


def regions(id_):
    r = ROWS[id_]
    return set(r['primary']), set(r['secondary'])


class V2Rules(unittest.TestCase):
    def test_seated_calf_is_soleus(self):
        p, s = regions('0088')                       # barbell seated calf raise
        self.assertEqual(p, {'soleus'})
        self.assertIn('calves', s)

    def test_standing_calf_keeps_both(self):
        ids = [k for k, v in ROWS.items() if v['name'] == 'lever standing calf raise' and 'variantOf' not in v]
        self.assertTrue(ids)
        p, _ = regions(ids[0])
        self.assertLessEqual({'calves', 'soleus'}, p)

    def test_hammer_curl_adds_brachialis(self):
        p, _ = regions('0166')                       # cable hammer curl
        self.assertLessEqual({'biceps', 'brachialis', 'forearm'}, p)

    def test_reverse_curl_moves_biceps_to_secondary(self):
        p, s = regions('0080')                       # barbell reverse curl
        self.assertLessEqual({'brachialis', 'forearm'}, p)
        self.assertNotIn('biceps', p)
        self.assertIn('biceps', s)

    def test_plain_curl_has_no_brachialis_primary(self):
        ids = [k for k, v in ROWS.items() if v['name'] == 'dumbbell biceps curl' and 'variantOf' not in v]
        self.assertTrue(ids)
        self.assertNotIn('brachialis', regions(ids[0])[0])

    def test_overhead_triceps_is_long_head(self):
        p, s = regions('0092')                       # barbell seated overhead triceps extension
        self.assertEqual(p, {'tricepsLongHead'})
        self.assertIn('triceps', s)

    def test_hip_abduction_is_gluteus_medius(self):
        p, _ = regions('4031')                       # band hip abduction
        self.assertIn('gluteusMedius', p)
        self.assertNotIn('gluteal', p)

    def test_squat_does_not_light_gluteus_medius(self):
        rows = [v for v in ROWS.values() if v['name'] == 'barbell full squat' and 'variantOf' not in v]
        self.assertTrue(rows)
        for v in rows:
            self.assertNotIn('gluteusMedius', v['primary'] + v['secondary'])

    def test_lat_pulldown_lights_teres_major(self):
        p, _ = regions('2330')                       # cable lat pulldown full range of motion
        self.assertLessEqual({'upperBack', 'teresMajor'}, p)

    def test_upper_back_no_longer_holds_rotator_cuff(self):
        self.assertNotIn('rotatorCuff', B.G['upper-back'])
        self.assertIn('rotatorCuff', B.G['deltoids'])

    def test_lateral_raise_does_not_light_rotator_cuff(self):
        rows = [v for v in ROWS.values() if v['name'] == 'dumbbell lateral raise' and 'variantOf' not in v]
        self.assertTrue(rows)
        for v in rows:
            self.assertNotIn('rotatorCuff', v['primary'])

    def test_neck_flexion_and_extension(self):
        self.assertEqual(regions('10780')[0], {'sternocleidomastoid'})      # lying neck flexion
        self.assertEqual(regions('2411')[0], {'neckBack'})                  # cable seated neck extension
        self.assertEqual(regions('2283')[0], {'sternocleidomastoid', 'neckBack'})  # side flexion

    def test_every_region_is_named_and_mapped(self):
        rows = B.regions_v2_rows()
        self.assertEqual(len(rows), 36)
        watch = {r['watchGroup'] for r in rows} - {None}
        self.assertEqual(len(watch), 18)
        self.assertEqual({r['region'] for r in rows if r['watchGroup'] is None}, {'sternocleidomastoid', 'neckBack'})

    def test_regions_v2_json_is_current(self):
        committed = json.loads((B.HERE / 'regions_v2.json').read_text(encoding='utf-8'))
        self.assertEqual(committed, B.regions_v2_rows())


if __name__ == '__main__':
    unittest.main()

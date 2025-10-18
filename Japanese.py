import csv
import inspect
import os
import re
import sys
import random

import BossSpawns
import CommonContent
import Equipment
import Game
import Level
import Monsters
import Mutators
import RareMonsters
import Shrines
import Spells
import text
import traceback

print("Japanese Mod 2.3.0 Loaded")

frm = inspect.stack()[-1]
RiftWizard = inspect.getmodule(frm[0])


def load_dics():
	for f in os.listdir("mods/Japanese/dics"):
		dic_name = os.path.splitext(f)[0]
		dics[dic_name] = {}
		with open(f"mods/japanese/dics/{f}", "r", encoding="shift-jis") as file:
			reader = csv.reader(file, delimiter="\t")
			for row in reader:
				if len(row) > 2 and row[2]:
					key, val = row[1], row[2]
					dics[dic_name][key] = val

dics = {}
load_dics()

dics_to_replace_numbers = {"spell_description", "skill_description", "buff_name", "buff_description", "monster_spell_description", "equipment_description", "trial_name", "trial_description", "cloud_description", "item_description", "log_name", "custom_name", "upgrade_description"}

dics["spell_name"].update(dics["item_name"])
dics["spell_description"].update(dics["item_description"])

dics["monster_spell_name"].update(dics["spell_name"])
dics["monster_spell_description"].update(dics["spell_description"])

dics["buff_name"].update(dics["spell_name"])
dics["buff_name"].update(dics["skill_name"])

dics["purchase_name"] = {}
dics["purchase_name"].update(dics["spell_name"])
dics["purchase_name"].update(dics["skill_name"])
dics["purchase_name"].update(dics["upgrade_name"])
dics["purchase_name"].update(dics["equipment_name"])

dics["log_name"] = {}
dics["log_name"].update(dics["spell_name"])
dics["log_name"].update(dics["skill_name"])
dics["log_name"].update(dics["upgrade_name"])
dics["log_name"].update(dics["equipment_name"])
dics["log_name"].update(dics["monster_name"])
dics["log_name"].update(dics["monster_spell_name"])
dics["log_name"].update(dics["buff_name"])
dics["log_name"].update(dics["item_name"])
dics["log_name"].update(dics["cloud_name"])
dics["log_name"].update(dics["trial_name"])

dics["custom_param"].update(dics["monster_name"])
dics["custom_param"].update(dics["tag_name"])
dics["custom_param"].update(dics["shrine_name"])
dics["custom_param"].update(dics["buff_name"])
dics["custom_param"].update(dics["attr_name"])


def translate(string, dic):

	if string == "":
		return ""
	if len(string) <= 2 or not string[0].isascii() or not string[1].isascii() or not string[2].isascii() or string.isdigit():
		return string
	original_string = string
	string = string.strip()
	translated = ""
	exp = r"-?\d+"
	numbers = re.findall(exp, string)
	if dic.endswith("name") or dic.endswith("param") :
		string = string.lower().replace('_', ' ')
	if dic in dics_to_replace_numbers:
		for num in numbers:
			string = string.replace(num, "*", 1)
	if dic in dics:
		for key in dics[dic].keys():
			if key == string:
				translated = dics[dic][key]
				break
	else:
		print("辞書がありません \"%s\"" % dic)

	# 一致するテキストがない場合
	if translated == "":
		if dic == "monster_name" or dic == "log_name":
			prefix_exp = r"(\b\w+\s+)(.*?$)"
			prefix_match = re.match(prefix_exp, string)
			if prefix_match:
				prefix = prefix_match.group(1)
				suffix = prefix_match.group(2)
				translated_prefix = translate(prefix, "monster_prefix")
				if not translated_prefix[0].isascii():
					translated_suffix = translate(suffix, dic)
					return translated_prefix + translated_suffix
			suffix_exp = r"^(.*?)(\s+\w+\b)(?=\s*$)"
			suffix_match = re.match(suffix_exp, string)
			if suffix_match:
				prefix = suffix_match.group(1)
				suffix = suffix_match.group(2)
				translated_suffix = translate(suffix, "monster_suffix")
				if not translated_suffix[0].isascii():
					translated_prefix = translate(prefix, dic)
					return translated_prefix + translated_suffix
			# Reverse order search
			reversed_prefix_exp = r"(.*?\s+)(\b\w+$)"
			reversed_prefix_match = re.match(reversed_prefix_exp, string)
			if reversed_prefix_match:
				suffix = reversed_prefix_match.group(1)
				prefix = reversed_prefix_match.group(2)
				translated_suffix = translate(suffix, "monster_suffix")
				if not translated_suffix[0].isascii():
					translated_prefix = translate(prefix, dic)
					return translated_prefix + translated_suffix
			reversed_suffix_exp = r"^(\w+\s+)(.*?$)"
			reversed_suffix_match = re.match(reversed_suffix_exp, string)
			if reversed_suffix_match:
				suffix = reversed_suffix_match.group(1)
				prefix = reversed_suffix_match.group(2)
				translated_prefix = translate(prefix, "monster_prefix")
				if not translated_prefix[0].isascii():
					translated_suffix = translate(suffix, dic)
					return translated_prefix + translated_suffix
		if dic == "equipment_name" or dic == "purchase_name" or dic == "log_name":
			prefix_exp = r"mini (.*?$)"
			prefix_match = re.match(prefix_exp, string)
			if prefix_match:
				base_equipment_name = prefix_match.group(1)
				return "ミニ・"+translate(base_equipment_name, "equipment_name")

		if dic != "monster_prefix" and dic != "monster_suffix":
			print("訳がありません", dic, string)
	else:
		for num in numbers:
			translated = translated.replace("*", num, 1)
		return translated
	return original_string

def translate_with_tag(string):
	dic = "tag_name"

	if string == "":
		return ""
	if len(string) <= 2 or not string[0].isascii() or not string[1].isascii() or not string[2].isascii() or string.isdigit():
		return string
	original_string = string
	translated = ""
	string = string.strip().lower().replace('_', ' ')
	for key in dics[dic].keys():
		if key == string:
			translated = dics[dic][key]
			break

	# 一致するテキストがない場合
	if translated == "":
		print("訳がありません", dic, string)
	else:
		return "["+translated+":"+string+"]"
	return original_string


def translate_lines(string, dic):
	if string is None:
		return ""
	lines = string.split("\n")
	translated_lines = []
	for line in lines:
		translated_line = translate(line, dic)
		translated_lines.append(translated_line)
	return "\n".join(translated_lines)


# CommonContent.py

def common_content_simple_summon_calc_text(self):
	spawn_name = translate(self.spawn_func().name, "monster_name")

	if self.num_summons > 1:
		spawn_name += "たち"

	self.name = "%sの召喚" % spawn_name

	if self.duration:
		spawn_name = "一時的な" + spawn_name

	if self.num_summons == 1:
		self.description = "%sを召喚する。" % spawn_name
	else:
		self.description = "%d体の%sを召喚する。" % (self.num_summons, translate(spawn_name, "monster_name"))

	if self.global_summon:
		self.description = "マップのランダムな位置に" + self.description

	if self.max_channel:
		self.description += "\n最大%dターン連続詠唱できる。" % self.max_channel

CommonContent.SimpleSummon.calc_text = common_content_simple_summon_calc_text


def common_content_heal_ally_overwrite(cls):
	original_init = cls.__init__
	def new_init(self, *args, **kwargs):
		original_init(self, *args, **kwargs)
		self.name = "味方の回復"
		self.description = "自分または味方1体を %d 回復する" % self.heal
		if self.range == 0:
			self.description = "自分を %d 回復する" % self.heal
			self.can_target_self = True
		if self.tag:
			self.description = "%sの味方1体を %d 回復する" % (translate(self.tag.name, "tag_name"), self.heal)

	cls.__init__ = new_init
	return cls
	
CommonContent.HealAlly = common_content_heal_ally_overwrite(CommonContent.HealAlly)


def common_content_cloud_generator_overwrite(cls):
	original_init = cls.__init__
	def new_init(self, *args, **kwargs):
		original_init(self, *args, **kwargs)
		self.description = "%sを%dタイル以内に生成する。" % (translate(self.cloud_func(None).name, "cloud_name"), self.radius)

	cls.__init__ = new_init
	return cls
	
CommonContent.CloudGeneratorBuff = common_content_cloud_generator_overwrite(CommonContent.CloudGeneratorBuff)


def common_content_damage_aura_overwrite(cls):
	original_init = cls.__init__
	def new_init(self, *args, **kwargs):
		original_init(self, *args, **kwargs)
		custom_name = kwargs.get("custom_name")
		if custom_name: self.name = custom_name
		elif isinstance(self.damage_type, RiftWizard.Tag): self.name = "%s・オーラ" % translate(self.damage_type.name, "tag_name")
		else: self.name = "ダメージ・オーラ"

	cls.__init__ = new_init

	def new_get_tooltip(self):
		damage_type_str = "か".join(translate(t.name, "tag_name") for t in self.damage_type) if isinstance(self.damage_type, list) else translate(self.damage_type.name, "tag_name")
		unit_type_str = "ユニット" if self.friendly_fire else "敵ユニット"
		return "毎ターン、%d%sダメージを半径%dタイル内の%sに与える。" % (self.damage, damage_type_str, self.radius, unit_type_str)
	cls.get_tooltip = new_get_tooltip

	return cls
	
CommonContent.DamageAuraBuff = common_content_damage_aura_overwrite(CommonContent.DamageAuraBuff)


def common_content_thorns_overwrite(cls):
	original_init = cls.__init__
	def new_init(self, *args, **kwargs):
		original_init(self, *args, **kwargs)
		self.description = "近接攻撃してきた相手に%d%sダメージを与える。" % (self.damage, translate(self.dtype.name, "tag_name"))

	cls.__init__ = new_init
	return cls
	
CommonContent.Thorns = common_content_thorns_overwrite(CommonContent.Thorns)


def common_content_retaliation_buff_overwrite(cls):
	original_init = cls.__init__
	def new_init(self, *args, **kwargs):
		original_init(self, *args, **kwargs)
		self.name = "%s・リタリエーション" % translate(self.dtype.name, "tag_name")
		self.description = "これを傷つけた敵ユニットに%d%sダメージを与える。" % (self.damage, translate_with_tag(self.dtype.name))

	cls.__init__ = new_init
	return cls
	
CommonContent.RetaliationBuff = common_content_retaliation_buff_overwrite(CommonContent.RetaliationBuff)



def common_content_chance_to_become_on_init(self):
	name = self.spawn_name if self.spawn_name else self.spawner().name
	self.description = "毎ターン%d%%の確率で%sになる。" % (self.chance * 100, translate(name, "monster_name"))

CommonContent.ChanceToBecome.on_init = common_content_chance_to_become_on_init



def common_content_mature_into_get_tooltip(self):
	if not self.spawn_name:
		self.spawn_name = self.spawner().name
	return "%dターン後に%sになる。" % (self.mature_duration, translate(self.spawn_name, "monster_name"))

CommonContent.MatureInto.get_tooltip = common_content_mature_into_get_tooltip


def common_content_spawn_on_death_overwrite(cls):
	original_init = cls.__init__
	def new_init(self, *args, **kwargs):
		original_init(self, *args, **kwargs)
		self.description = "死亡時、%d体の%sを生む。" % (self.num_spawns, translate(self.spawner().name, "monster_name"))

	cls.__init__ = new_init

	def new_get_tooltip(self):
		return "死亡時、%d体の%sを生む。" % (self.num_spawns, translate(self.spawner().name, "monster_name"))
	cls.get_tooltip = new_get_tooltip

	return cls
	
CommonContent.SpawnOnDeath = common_content_spawn_on_death_overwrite(CommonContent.SpawnOnDeath)


def common_content_respawn_as_overwrite(cls):
	original_init = cls.__init__
	def new_init(self, *args, **kwargs):
		original_init(self, *args, **kwargs)
		self.name = "%sとして復活" % translate(self.spawn_name, "monster_name")
	cls.__init__ = new_init

	def new_get_tooltip(self):
		if not self.spawn_name:
			self.spawn_name = self.spawner().name
		return "HPが0になったとき、%sに変身する。" % translate(self.spawn_name, "monster_name")
	cls.get_tooltip = new_get_tooltip

	return cls
	
CommonContent.RespawnAs = common_content_respawn_as_overwrite(CommonContent.RespawnAs)


def common_content_death_explosion_overwrite(cls):
	original_init = cls.__init__
	def new_init(self, *args, **kwargs):
		original_init(self, *args, **kwargs)
		self.description = "死亡時、%d%sダメージを半径%dタイル内のすべてのタイルに与える。" % (self.damage, translate(self.damage_type.name, "tag_name"), self.radius)

	cls.__init__ = new_init
	return cls

CommonContent.DeathExplosion = common_content_death_explosion_overwrite(CommonContent.DeathExplosion)


def common_content_touched_by_sorcery_overwrite(cls):
	original_on_init = cls.on_init
	def new_on_init(self, *args, **kwargs):
		original_on_init(self, *args, **kwargs)
		self.name = "%sによる接触" % translate(self.element.name, "tag_name")

	cls.on_init = new_on_init
	return cls

CommonContent.TouchedBySorcery = common_content_touched_by_sorcery_overwrite(CommonContent.TouchedBySorcery)


def common_content_adaptive_armor_resist_buff_overwrite(cls):
	original_init = cls.__init__
	def new_init(self, *args, **kwargs):
		original_init(self, *args, **kwargs)
		if args != None:
			self.name = "%s・アーマー" % translate(args[0].name, "tag_name")
		else:
			self.name = "%s・アーマー" % translate(kwargs.get("tag").name, "tag_name")

	cls.__init__ = new_init
	return cls

CommonContent.AdaptiveArmorResistBuff = common_content_adaptive_armor_resist_buff_overwrite(CommonContent.AdaptiveArmorResistBuff)

def common_content_generator_2_buff_get_tooltip(self):
	return "%s1体を%dから%dターンごとに生む。\n\n次の発生：%dターン" % (translate(self.example_monster.name, "monster_name"), self.min_turns, self.max_turns, self.turns)

CommonContent.Generator2Buff.get_tooltip = common_content_generator_2_buff_get_tooltip


def common_content_touched_by_sorcery_on_init(self):
	self.resists[self.element] = 100
	self.name = "タッチド・バイ・%s" % translate(self.element.name, "tag_name")
	self.color = self.element.color
	spell = RiftWizard.SimpleRangedAttack(damage=5, range=7, damage_type=self.element)
	spell.name = "ソーサリー"
	self.spells = [spell]
	self.asset = ["status", "%s_eye" % self.element.name.lower()]

CommonContent.TouchedBySorcery.on_init = common_content_touched_by_sorcery_on_init


# ConeTest.py
# Consumables.py
# Equipment.py

# NOTE: Equipment.FangedAmulet.get_description

def equipment_generic_frenzy_stack_init(self, tag, damage):
	RiftWizard.Buff.__init__(self)
	self.name = "%s・フレンジー" % translate(tag.name, "tag_name")
	self.color = tag.color
	self.stack_type = RiftWizard.STACK_INTENSITY
	self.tag_bonuses[tag]["damage"] = damage


Equipment.GenericFrenzyStack.__init__ = equipment_generic_frenzy_stack_init


def equipment_generic_oculus_debuff_init(self, tag):
	RiftWizard.Buff.__init__(self)
	self.buff_type = RiftWizard.BUFF_TYPE_CURSE
	self.color = tag.color
	self.name = "%s弱点" % translate(tag.name, "tag_name")
	self.stack_type = RiftWizard.STACK_NONE
	self.resists[tag] = -25


Equipment.GenericOculusDebuff.__init__ = equipment_generic_oculus_debuff_init


def eqipment_pet_collar_on_init(self):
	self.name = "エキゾチック・ペット"
	self.description = "各レルムの最初に%sを召喚する" % translate(self.example.name, "monster_name")
	self.owner_triggers[RiftWizard.EventOnUnitAdded] = self.on_add
	self.slot = RiftWizard.ITEM_SLOT_AMULET
	self.is_pet = True 

Equipment.PetCollar.on_init = eqipment_pet_collar_on_init


def eqipment_cultists_staff_do_damage(self):
	o = self.owner
	lvl = self.owner.level

	if o.cur_hp <= 1: return # return if you can't afford to pay life

	shortest_dist = None
	candidates = []

	for u in lvl.units:
		if not (RiftWizard.are_hostile(u, o) and u.is_alive()): continue
		dist_u = RiftWizard.distance(u, o)
		if shortest_dist is None or dist_u < shortest_dist:
			shortest_dist = dist_u
			candidates = [u]
		elif dist_u == shortest_dist: candidates.append(u)

	if not candidates: return
	unit = random.choice(candidates)

	# spend the hp
	o.cur_hp -= 1
	lvl.combat_log.debug("%sは%dHP支払って%sを唱えた。" % (translate(o.name, "log_name"), 1, translate(self.name, "log_name")))
	lvl.event_manager.raise_event(RiftWizard.EventOnSpendHP(o, 1), o)
	lvl.show_effect(o.x, o.y, RiftWizard.Tags.Blood, minor=True)


	o.level.show_path_effect(o, unit, RiftWizard.Tags.Dark, minor=True)
	missing_hp = o.max_hp - o.cur_hp
	unit.deal_damage(missing_hp, RiftWizard.Tags.Dark, self)
	yield

Equipment.CultistsStaff.do_damage = eqipment_cultists_staff_do_damage


def equipment_pet_sigil_on_init(self):
	self.name = "%s・シジル" % translate(self.example.name, "monster_name")
	self.description = "各レルムの最初に%sのスポナーを召喚する" % translate(self.example.name, "monster_name")
	self.owner_triggers[RiftWizard.EventOnUnitAdded] = self.on_add
	self.slot = RiftWizard.ITEM_SLOT_AMULET
	self.asset_name = "trinket_sigil"
	self.is_pet = True 


Equipment.PetSigil.on_init = equipment_pet_sigil_on_init


# FinalBosses.py
# Game.py
def game_finalize_level(self, victory):
	filename = os.path.join("saves", str(self.run_number), "stats.level_%d.txt" % self.level_num)
	self.total_turns += self.cur_level.turn_no

	dirname = os.path.dirname(filename)
	if not os.path.exists(dirname):
		os.makedirs(dirname)

	self.rift_rerolls = 1

	with open(filename, "w") as stats:
		stats.write("レルム %d\n" % self.level_num)
		if self.trial_name:
			stats.write(translate(self.trial_name, "trial_name") + "\n")
		stats.write("結果：%s\n" % ("勝利" if victory else "敗北"))
		stats.write("\nターン数\n")
		stats.write("%d（現在）\n" % self.cur_level.turn_no)
		stats.write("%d（累計）\n" % self.total_turns)

		spell_counts = sorted(self.cur_level.spell_counts.items(), key=lambda t: -t[1])
		if spell_counts:
			stats.write("\n呪文詠唱回数：\n")
			for s, c in spell_counts:
				stats.write("%3d %s\n" % (c, translate(s, "spell_name")))

		dealers = sorted(self.cur_level.damage_dealt_sources.items(), key=lambda t: -t[1])
		if dealers:
			stats.write("\n与えたダメージ：\n")
			for s, d in dealers[:5]:
				stats.write("%d %s\n" % (d, translate(s, "log_name")))
			if len(dealers) > 6:
				total_other = sum(d for s, d in dealers[5:])
				stats.write("%d その他\n" % total_other)

		sources = sorted(self.cur_level.damage_taken_sources.items(), key=lambda t: -t[1])
		if sources:
			stats.write("\n受けたダメージ：\n")
			for s, d in sources[:5]:
				stats.write("%d %s\n" % (d, translate(s, "log_name")))
			if len(sources) > 6:
				total_other = sum(d for s, d in sources[5:])
				stats.write("%d その他\n" % total_other)

		item_counts = sorted(self.cur_level.item_counts.items(), key=lambda t: -t[1])
		if item_counts:
			stats.write("\n使ったアイテム：\n")
			for s, c in item_counts:
				stats.write("%d %s\n" % (c, translate(s, "item_name")))

		if self.recent_upgrades:
			stats.write("\n獲得したもの：\n")
			for u in self.recent_upgrades:
				fmt = translate(u.name, "purchase_name")
				if getattr(u, "prereq", None):
					fmt = "%s %s" % (translate(u.prereq.name, "purchase_name"), translate(u.name, "purchase_name"))
				stats.write("%s\n" % fmt)

		self.recent_upgrades.clear()

Game.Game.finalize_level = game_finalize_level


# GenerateInfo.py
# Level.py
def level_spell_pay_costs(self):

	if self.item:
		self.caster.remove_item(self.item)
		return

	self.caster.mana = self.caster.mana - self.get_mana_cost()
	if self.cool_down > 0:
		self.caster.cool_downs[self] = self.cool_down

	if self.max_charges:
		self.cur_charges -= 1

	hp_cost = self.get_stat('hp_cost')
	if hp_cost:
		self.caster.cur_hp -= hp_cost
		self.caster.level.combat_log.debug("%sは%dHP支払って%sを唱えた。" % (translate(self.caster.name, "log_name"), hp_cost, translate(self.name, "log_name")))
		self.caster.level.event_manager.raise_event(RiftWizard.EventOnSpendHP(self.caster, hp_cost), self.caster)
		self.caster.level.show_effect(self.caster.x, self.caster.y, RiftWizard.Tags.Blood, minor = hp_cost < 11)

Level.Spell.pay_costs = level_spell_pay_costs


def level_unit_advance(self, orders=None):

	can_act = True
	for b in self.buffs:
		if not b.on_attempt_advance():
			can_act = False
			if self.is_player_controlled:
				stun_duration = 1 if not isinstance(self.last_action, RiftWizard.StunnedAction) else self.last_action.duration + 1
				self.last_action = RiftWizard.StunnedAction(b, stun_duration)
				self.level.requested_action = None
				self.level.combat_log.debug("[あなた:wizard]は%sしていた。" % translate(b.name, "log_name"))

	if can_act:
		# Take an action
		if not self.is_player_controlled:
			action = self.get_ai_action()
		else:
			action = self.level.requested_action
			self.level.requested_action = None
			self.last_action = action

		if action:
			RiftWizard.logging.debug("%s will %s" % (self, action))

		if isinstance(action, RiftWizard.MoveAction):
			if self.is_player_controlled:
				self.level.combat_log.debug("[あなた:wizard]は歩いた。")
			self.level.act_move(self, action.x, action.y)
			if self.quick_move and not self.quick_cast_used:
				self.quick_cast_used = True
				return False
		elif isinstance(action, RiftWizard.CastAction):
			self.level.act_cast(self, action.spell, action.x, action.y)
			if action.spell.get_stat("quick_cast") and not self.quick_cast_used:
				self.quick_cast_used = True
				return False
		elif isinstance(action, RiftWizard.PassAction):
			if self.is_player_controlled:
				self.level.combat_log.debug("[あなた:wizard]は待機した。")
			self.level.event_manager.raise_event(RiftWizard.EventOnPass(self), self)

	self.try_dismiss_ally()

	return True

Level.Unit.advance = level_unit_advance


def level_unit_apply_buff(self, buff, duration=0):
	assert isinstance(buff, RiftWizard.Buff)

	# If we call this method before adding the monster to the level just add the buff to the list and we will call this again later
	if not hasattr(self, 'level'): self.buffs.append(buff); return

	# Do not apply buffs to dead units
	if not self.is_alive(): return

	if self.clarity > 0 and buff.buff_type == RiftWizard.BUFF_TYPE_CURSE: self.clarity -= 1; return

	if not buff.on_attempt_apply(self): return

	if buff.buff_type == RiftWizard.BUFF_TYPE_CURSE and self.debuff_immune: return
	if buff.buff_type == RiftWizard.BUFF_TYPE_BLESS and self.buff_immune: return

	# Do not refresh stuns or silences on clarity havers
	# Otherwise they can get stunlocked by anything with 2 or more duration
	# Which defeats the purpose of clarity
	if self.gets_clarity and isinstance(buff, RiftWizard.Stun) and self.is_stunned(): return
	if self.gets_clarity and isinstance(buff, RiftWizard.Silence) and self.is_silenced(): return

	def same_buff(b1, b2):
		return b1.name == b2.name and type(b1) == type(b2)

	existing = [b for b in self.buffs if same_buff(b, buff)]
	if existing:

		if buff.stack_type == RiftWizard.STACK_NONE:
			if existing[0].turns_left > 0:
				existing[0].turns_left = max(duration, existing[0].turns_left)
				return
			else:
				return
		elif buff.stack_type == RiftWizard.STACK_DURATION:
			existing[0].turns_left += duration
			return
		elif buff.stack_type == RiftWizard.STACK_REPLACE:
			self.remove_buff(existing[0])
			# And continue to add this one

	if buff.stack_type == RiftWizard.STACK_TYPE_TRANSFORM:
		existing = [b for b in self.buffs if b != buff and b.stack_type == RiftWizard.STACK_TYPE_TRANSFORM]
		if existing:
			self.remove_buff(existing[0])

	assert isinstance(buff, RiftWizard.Buff)
	buff.turns_left = duration

	self.buffs.append(buff)
	result = buff.apply(self)
	if result == RiftWizard.ABORT_BUFF_APPLY:
		self.buffs.remove(buff)
		return

	if buff.show_effect:
		if buff.buff_type == RiftWizard.BUFF_TYPE_BLESS:
			if self.buff_immune:
				return
			self.level.show_effect(self.x, self.y, RiftWizard.Tags.Buff_Apply, buff.color)
		if buff.buff_type == RiftWizard.BUFF_TYPE_CURSE:
			if self.debuff_immune:
				return
			self.level.show_effect(self.x, self.y, RiftWizard.Tags.Debuff_Apply, buff.color)

		if buff.buff_type in (RiftWizard.BUFF_TYPE_BLESS, RiftWizard.BUFF_TYPE_CURSE):
			if self.level.player_unit:
				unit_log_color = "wizard" if self.is_player_controlled else "ally" if not RiftWizard.are_hostile(self, self.level.player_unit) else "enemy"
			else:
				unit_log_color = "enemy"
			self.level.combat_log.debug("[%s:%s]は[%dターン:duration]の%sを受けた。" % (translate(self.name, "log_name"), unit_log_color, duration, translate(buff.name, "log_name")))

	self.level.event_manager.raise_event(RiftWizard.EventOnBuffApply(buff, self), self)

Level.Unit.apply_buff = level_unit_apply_buff


def level_unit_steal_hp(self, amount, source):

	amount = min(self.cur_hp, amount)
	self.cur_hp -= amount

	self.event_manager.raise_event()

	if self.cur_hp <= 0:
		self.kill()

	self.level.show_effect(self.x, self.y, RiftWizard.Tags.Blood)

	source_name = "%s %s" % (source.owner.name, source.name) if source.owner else source.name
	self.level.combat_log.debug("%sは%sによって生命を%d失った。" % (translate(self.name, "log_name"), translate(source_name, "log_name"), amount))

	return amount

Level.Unit.steal_hp = level_unit_steal_hp


def level_level_act_cast(self, unit, spell, x, y, pay_costs=True, queue=True, is_echo=False):
	assert isinstance(unit, RiftWizard.Unit), "caster is not of type unit, is %s" % type(unit)

	if unit.is_player_controlled:
		if spell.item:
			self.item_counts[spell.name] += 1
		else:
			self.spell_counts[spell.name] += 1

	if self.player_unit:
		unit_color = "wizard" if unit.is_player_controlled else "ally" if not RiftWizard.are_hostile(unit, self.player_unit) else "enemy"
	else:
		unit_color = "enemy"
	self.combat_log.debug("[%s:%s]は%sを使った。" % (translate(unit.name, "log_name"), unit_color, translate(spell.name, "log_name")))

	# flip sprite if needed
	if x < unit.x:
		unit.sprite.face_left = True
	if x > unit.x:
		unit.sprite.face_left = False

	if pay_costs:
		assert spell.can_cast(x, y), "%s trying to cast spell %s on untargetable tile %d, %d" % (unit.name, spell.name, x, y)
		assert spell.can_pay_costs(), "%s trying to cast spell %s, but cannot pay costs" % (unit.name, spell.name)

	if pay_costs:
		spell.pay_costs()

	# If we want to queue the spell, queue it.  Else return the generator so the calling spell can iterate over it.
	if queue:
		if is_echo: self.queue_spell(spell.cast(x, y, is_echo=is_echo)); rval = None
		else: self.queue_spell(spell.cast(x, y)); rval = None
	else:
		rval = spell.cast(x, y)

	if not spell.item:
		self.event_manager.raise_event(RiftWizard.EventOnSpellCast(spell, unit, x, y, pay_costs), unit)
	if spell.item:
		self.event_manager.raise_event(RiftWizard.EventOnItemUsed(unit, spell.item), unit)

	return rval

Level.Level.act_cast = level_level_act_cast


def level_level_iter_frame(self, mark_turn_end=False):

	while self.can_advance_spells():
		yield self.advance_spells()

	# An iterator representing the order of turns for all game objects
	while True:

		self.damage_instances.clear() # reset the damage dict

		# Yield once per iteration if there are no units to prevent infinite loop
		if not self.units:
			yield

		self.turn_no += 1

		if any(u.team != RiftWizard.TEAM_PLAYER for u in self.units):
			self.next_log_turn()
			self.combat_log.debug("レルム %d、ターン %d 開始。" % (self.level_no, self.turn_no))

		# Cache unit list here to enforce summoning delay
		turn_units = list(self.units)
		for is_player_turn in [True, False]:
			clouds = [cloud for cloud in self.clouds if cloud.owner.is_player_controlled == is_player_turn]
			if clouds:
				for cloud in clouds:
					if cloud.is_alive:
						cloud.advance()
				while self.can_advance_spells():
					yield self.advance_spells()

			units = [unit for unit in turn_units if unit.is_player_controlled == is_player_turn]
			RiftWizard.random.shuffle(units)

			for unit in units:
				if not unit.is_alive():
					continue

				unit.pre_advance()

				finished_advance = False
				while not finished_advance:
					if unit.is_player_controlled and not unit.is_stunned() and not self.requested_action:
						self.is_awaiting_input = True
						yield

					# Yield for 1 frame if stunned to prevent jarring time skip
					if unit.is_player_controlled and unit.is_stunned():
						yield

					# Clear turn summary as soon as player chooses an action, before it is executed
					# But group all things happening during stuns together
					if unit.is_player_controlled and not unit.is_stunned():
						self.turn_summary.clear()

					finished_advance = unit.advance()

					# yield
					while self.can_advance_spells():
						yield self.advance_spells()

				# Advance buffs after advancing spells
				unit.advance_buffs()

				while self.can_advance_spells():
					yield self.advance_spells()

				self.frame_units_moved += 1

				# Yield if the current advance frame is aboive the advance time budget
				if RiftWizard.time.time() - self.frame_start_time > RiftWizard.MAX_ADVANCE_TIME:
					yield

		# Advance all props similtaneously
		for prop in list(self.props):
			prop.advance()

		# In the unlikely event that that created effects, advance them
		while self.can_advance_spells():
			yield self.advance_spells()

		if not RiftWizard.visual_mode:
			yield True

Level.Level.iter_frame = level_level_iter_frame


def level_level_deal_damage(self, x, y, amount, damage_type, source, flash=True, redirect=False):

	# Auto make effects if none were already made
	if flash:
		effect = RiftWizard.Effect(x, y, damage_type.color, RiftWizard.Color(0, 0, 0), 12)
		if amount == 0:
			effect.minor = True
		self.effects.append(effect)

	cloud = self.tiles[x][y].cloud
	if cloud and amount > 0:
		cloud.on_damage(damage_type)

	unit = self.get_unit_at(x, y)
	if not unit:
		return 0
	if not unit.is_alive():
		return 0

	# --- Redirection Hook ---
	if not redirect and hasattr(unit, "on_pre_damage_redirect"):
		result = unit.on_pre_damage_redirect(amount, damage_type, source)
		if result is not None:
			return result  # Damage was handled elsewhere

	unit_id = id(unit)
	if self.damage_instances[unit_id] >= RiftWizard.DAMAGE_INSTANCE_CAP:
		return 0
	
	# Raise pre damage event (for conversions)
	orig_amount = amount

	# Factor in shields and resistances after raising the raw pre damage event
	resist = unit.resists.get(damage_type, 0)

	# Cap effective resists at 100- shenanigans ensue if we do not
	resist = min(resist, 100)

	if resist:
		multiplier = (100 - resist) / 100.0
		amount = int(RiftWizard.math.ceil(amount * multiplier))

	pre_damage_event = RiftWizard.EventOnPreDamaged(unit, orig_amount, amount, damage_type, source)
	self.event_manager.raise_event(pre_damage_event, unit)

	# Logging strings
	unit_log_name = unit.name

	if self.player_unit:
		unit_log_color = "wizard" if unit.is_player_controlled else "ally" if not RiftWizard.are_hostile(unit, self.player_unit) else "enemy"
	else:
		unit_log_color = "enemy"

	source_str = source.name
	"%s %s" % (source.owner.name, source.name) if source.owner else source.name
	if source.owner:
		if self.player_unit:
			source_color = "wizard" if source.owner.is_player_controlled else "ally" if not RiftWizard.are_hostile(source.owner, self.player_unit) else "enemy"
		else:
			source_color = "enemy"

		source_owner_str = "[%s:%s]" % (translate(source.owner.name, "log_name"), source_color)

	if amount > 0 and unit.shields > 0:
		unit.shields = unit.shields - 1
		self.combat_log.debug("[%s:%s]は%sによる[%d%s:%s]ダメージをシールドで無効化した。" % (translate(unit_log_name, "log_name"), unit_log_color, translate(source_str, "log_name"), amount, translate(damage_type.name, "tag_name"), damage_type.name))
		self.show_effect(unit.x, unit.y, RiftWizard.Tags.Shield_Expire)
		evt = RiftWizard.EventOnShieldRemoved(unit)
		self.event_manager.raise_event(evt)
		return 0

	# Cap damage to current hp, cap healing to missing hp
	if amount > 0:
		amount = min(amount, unit.cur_hp)
	elif amount < 0:
		amount = max(amount, unit.cur_hp - unit.max_hp)

	unit.cur_hp = unit.cur_hp - amount

	unit_str = "[%s:%s]" % (translate(unit_log_name, "log_name"), unit_log_color)
	dmg_str = "[%d%s:%s]" % (amount, translate(damage_type.name, "tag_name"), damage_type.name)

	is_temp_buff = isinstance(source, RiftWizard.Buff) and source.buff_type in (RiftWizard.BUFF_TYPE_BLESS, RiftWizard.BUFF_TYPE_CURSE)

	# Logging
	if amount > 0:
		# Case 1, damage by spells or buffs with owners
		if source.owner and not is_temp_buff:
			self.combat_log.debug("%sは%sで%sに%sダメージを与えた。" % (source_owner_str, translate(source.name, "log_name"), unit_str, dmg_str))

		# Case 2, damage by spells or buffs without owners (aka: storm clouds, poison, ect)
		else:
			self.combat_log.debug("%sは%sによって%sダメージを受けた。" % (unit_str, translate(source.name, "log_name"), dmg_str))

	elif amount < 0:
		if not is_temp_buff:
			self.combat_log.debug("%sは%sで%sを[%d:heal]回復した。" % (source_owner_str, translate(source.name, "log_name"), unit_str, -amount))
		else:
			self.combat_log.debug("%sは%sによって[%d:heal]回復した。" % (unit_str, translate(source.name, "log_name"), -amount))

	# Processing
	if amount < 0:
		evt = RiftWizard.EventOnHealed(unit, amount, source)
		self.event_manager.raise_event(evt, unit)

	elif amount > 0:
		# Record damage sources when a player unit exists (aka not in unittests)
		if self.player_unit:
			# Enemy
			if RiftWizard.are_hostile(unit, self.player_unit):
				key = source.name
				if source.owner and source.owner.source and not (isinstance(source, RiftWizard.Buff) and source.buff_type == RiftWizard.BUFF_TYPE_CURSE):
					key = source.owner.name

				self.damage_dealt_sources[key] += amount
				self.turn_summary.damage_dealt[key] += amount
			# Ally/Self
			else:
				if isinstance(source, RiftWizard.Buff) and source.buff_type == RiftWizard.BUFF_TYPE_CURSE:
					key = source.name
				elif source.owner:
					key = source.owner.name
				else:
					key = source.name

				# Self
				if unit == self.player_unit:
					self.damage_taken_sources[key] += amount
					self.turn_summary.self_damage_taken[key] += amount
				# Ally
				else:
					self.turn_summary.ally_damage_taken[key] += amount

		damage_event = RiftWizard.EventOnDamaged(unit, amount, damage_type, source)
		self.event_manager.raise_event(damage_event, unit)

		if unit.cur_hp <= 0:
			unit.kill(damage_event=damage_event)

			if unit.cur_hp <= 0:
				unit.kill(damage_event=damage_event)

		if unit.cur_hp > unit.max_hp:
			unit.cur_hp = unit.max_hp
	# set amount to 0 if there is no unit- ie, if an empty tile or dead unit was hit
	else:
		amount = 0

	if unit.cur_hp > unit.max_hp:
		unit.cur_hp = unit.max_hp

	self.damage_instances[unit_id] += 1
	if self.damage_instances[unit_id] == RiftWizard.DAMAGE_INSTANCE_CAP:
		self.combat_log.debug("%sはこのターン、ユニットあたりのダメージキャップに到達した。" % unit_str)

	return amount

Level.Level.deal_damage = level_level_deal_damage


# LevelGen.py
# LevelGenHelpers.py
# monster_level_test.py
# Monsters.py

def monsters_spirit_buff_get_tooltip(self):
	return "視界内で%s呪文が詠唱されるたび、最大HPを5得る。" % translate(self.tag.name, "tag_name")

Monsters.SpiritBuff.get_tooltip = monsters_spirit_buff_get_tooltip



def monsters_slime_buff_init(self, spawner, name='slimes', growth_chance=.5):
	RiftWizard.Buff.__init__(self)
	self.description = ("毎ターン50%%の確率で元の最大HPの10%%を回復する。\n"
						"この効果による過剰な回復は最大HPを増加させる。\n"
						"最大HPが2倍になったとき、%s2体に分裂する。") % (translate(name, "monster_name"))
	self.name = "スライム成長"
	self.color = RiftWizard.Tags.Slime.color
	self.spawner = spawner
	self.spawner_name = name
	self.growth_chance = growth_chance

Monsters.SlimeBuff.__init__ = monsters_slime_buff_init


original_on_applied = Monsters.SlimeBuff.on_applied
def monsters_slime_buff_on_applied(self, *args, **kwargs):
	original_on_applied(self, *args, **kwargs)
	self.description = ("毎ターン50%%の確率でHPを%d回復する。\n"
						"この効果による過剰な回復は最大HPを増加させる。\n"
						"最大HPが%dになったとき、%s2体に分裂する。") % (self.growth, self.to_split, translate(self.spawner_name, "monster_name"))
	
Monsters.SlimeBuff.on_applied = monsters_slime_buff_on_applied



def monsters_generator_buff_get_tooltip(self):
	return "毎ターン%d%%の確率で%s1体を生む。" % (int(100 * self.spawn_chance), translate(self.spawner().name, "monster_name"))

Monsters.GeneratorBuff.get_tooltip = monsters_generator_buff_get_tooltip


def monsters_mushboom_buff_on_init(self):
	self.owner_triggers[RiftWizard.EventOnDeath] = self.on_death
	self.description = "死亡時、%dターンの%sを周囲のユニットたちに与える。" % (self.apply_duration, translate(self.buff().name, "buff_name"))
	self.name = "マッシュブーム・バースト"

Monsters.MushboomBuff.on_init = monsters_mushboom_buff_on_init


def monsters_vengeance_buff_on_init(self):
	self.color = RiftWizard.Tags.Dark.color
	self.name = "ベンジェンス"
	self.description = "死亡時、%d%sダメージをランダムな%dタイル以内のランダムな敵1体に与える。" % (self.damage, translate(self.damage_type.name, "tag_name"), self.radius)
	self.owner_triggers[RiftWizard.EventOnDeath] = self.on_death

Monsters.VengeanceBuff.on_init = monsters_vengeance_buff_on_init


# Mutators.py

def mutators_enemy_buff_overwrite(cls):
	original_init = cls.__init__
	def new_init(self, *args, **kwargs):
		original_init(self, *args, **kwargs)
		self.description = "すべての敵ユニットが「%s」を持つ" % translate(self.buff().name, "buff_name")
		self.placeholder_description = "すべての敵ユニットが「X」を持つ"

	cls.__init__ = new_init
	return cls
	
Mutators.EnemyBuff = mutators_enemy_buff_overwrite(Mutators.EnemyBuff)


def mutators_respawn_as_mutator_overwrite(cls):
	original_init = cls.__init__
	def new_init(self, *args, **kwargs):
		original_init(self, *args, **kwargs)
		self.description = "すべてのユニットが%sとして復活する" % translate(self.example_monster.name, "monster_name")
		self.placeholder_description = "すべての敵ユニットがXとして復活する"

	cls.__init__ = new_init
	return cls
	
Mutators.RespawnAsMutator = mutators_respawn_as_mutator_overwrite(Mutators.RespawnAsMutator)

def mutators_spell_tag_restriction_overwrite(cls):
	original_init = cls.__init__
	def new_init(self, *args, **kwargs):
		original_init(self, *args, **kwargs)
		self.description = "%sの呪文しか習得できない" % translate(self.tag.name, "tag_name")
		self.placeholder_description = "Xの呪文しか習得できない"

	cls.__init__ = new_init
	return cls
	
Mutators.SpellTagRestriction = mutators_spell_tag_restriction_overwrite(Mutators.SpellTagRestriction)

def mutators_spell_tag_elimination_overwrite(cls):
	original_init = cls.__init__
	def new_init(self, *args, **kwargs):
		original_init(self, *args, **kwargs)
		self.description = "すべての%sの呪文は除外される" % translate(self.tag.name, "tag_name")
		self.placeholder_description = "すべてのXの呪文は除外される"

	cls.__init__ = new_init
	return cls
	
Mutators.SpellTagElimination = mutators_spell_tag_elimination_overwrite(Mutators.SpellTagElimination)

def mutators_skill_tag_restriction_overwrite(cls):
	original_init = cls.__init__
	def new_init(self, *args, **kwargs):
		original_init(self, *args, **kwargs)
		self.description = "%sのスキルしか習得できない" % translate(self.tag.name, "tag_name")
		self.placeholder_description = "Xのスキルしか習得できない"

	cls.__init__ = new_init
	return cls
	
Mutators.SkillTagRestriction = mutators_skill_tag_restriction_overwrite(Mutators.SkillTagRestriction)

def mutators_skill_tag_elimination_overwrite(cls):
	original_init = cls.__init__
	def new_init(self, *args, **kwargs):
		original_init(self, *args, **kwargs)
		self.description = "すべての%sのスキルは除外される" % translate(self.tag.name, "tag_name")
		self.placeholder_description = "すべてのXのスキルは除外される"

	cls.__init__ = new_init
	return cls
	
Mutators.SkillTagElimination = mutators_skill_tag_elimination_overwrite(Mutators.SkillTagElimination)


def mutators_spell_stat_multiplier_overwrite(cls):
	original_init = cls.__init__
	def new_init(self, *args, **kwargs):
		original_init(self, *args, **kwargs)
		self.description = "呪文の%sは%d%%になる" % (translate(self.stat, "custom_param"), self.mult*100)
		self.placeholder_description = "呪文のXはX%になる" 

	cls.__init__ = new_init
	return cls
	
Mutators.SpellStatMultiplier = mutators_spell_stat_multiplier_overwrite(Mutators.SpellStatMultiplier)


def mutators_extra_spawns_overwrite(cls):
	original_init = cls.__init__
	def new_init(self, *args, **kwargs):
		original_init(self, *args, **kwargs)
		self.description = "最初の階層より後では追加で%sが%d体登場する" % (translate(self.spawn().name, "monster_name"), self.num_extra)
		self.placeholder_description = "最初の階層より後では追加でXがX体登場する" 

	cls.__init__ = new_init
	return cls
	
Mutators.ExtraSpawns = mutators_extra_spawns_overwrite(Mutators.ExtraSpawns)


def mutators_fixed_rewards_overwrite(cls):
	original_init = cls.__init__
	def new_init(self, *args, **kwargs):
		original_init(self, *args, **kwargs)
		self.description = "すべての階層の報酬は%sになる" % translate(self.reward, "custom_param")
		self.placeholder_description = "すべての階層の報酬はXになる" 

	cls.__init__ = new_init
	return cls
	
Mutators.FixedRewards = mutators_fixed_rewards_overwrite(Mutators.FixedRewards)


def mutators_fixed_rewards_overwrite(cls):
	original_init = cls.__init__
	def new_init(self, *args, **kwargs):
		original_init(self, *args, **kwargs)
		self.description = "すべての階層の報酬から%sが削除される" % translate(self.reward, "custom_param")
		self.placeholder_description = "すべての階層の報酬からXが削除される" 

	cls.__init__ = new_init
	return cls
	
Mutators.RemoveRewards = mutators_fixed_rewards_overwrite(Mutators.RemoveRewards)




# NPCs.py
# opengltest.py
# RareMonsters.py
def rare_monsters_idol_of_weakness_debuff_on_init(self):
	self.name = "%s・ウィークネス" % translate(self.tag.name, "tag_name")
	self.stack_type = RiftWizard.STACK_INTENSITY
	self.buff_type = RiftWizard.BUFF_TYPE_CURSE
	self.color = self.tag.color
	self.resists[self.tag] = -25

RareMonsters.IdolOfWeaknessDebuff.on_init = rare_monsters_idol_of_weakness_debuff_on_init


def rare_monsters_scale_woven_on_init(self):
	self.resists[self.immunity_tag] = 100
	self.name = "%s・ウォーブン" % translate(self.immunity_tag.name, "tag_name")
	self.color = self.immunity_tag.color
	self.buff_type = RiftWizard.BUFF_TYPE_BLESS

RareMonsters.ScaleWoven.on_init = rare_monsters_scale_woven_on_init

# RiftWizard2.py

old_init = RiftWizard.PyGameView.__init__
def pygameview_init(self, *args, **kwargs):
	old_init(self, *args, **kwargs)
	RiftWizard.pygame.font.init()
	font_path = os.path.join("mods", "Japanese", "font.ttf")
	self.font = RiftWizard.pygame.font.Font(font_path, 16)

RiftWizard.PyGameView.__init__ = pygameview_init


def draw_char_sheet(self):
	self.middle_menu_display.fill((0, 0, 0))
	self.draw_panel(self.middle_menu_display)

	# Spells
	spell_x_offset = self.border_margin + 18
	cur_x = spell_x_offset
	cur_y = self.linesize
	self.draw_string("呪文", self.middle_menu_display, cur_x, cur_y)

	m_loc = self.get_mouse_pos()

	cur_y += self.linesize
	cur_y += self.linesize
	spell_index = 0

	col_width = self.middle_menu_display.get_width() // 2 - 2 * self.border_margin

	# Spells
	for spell in self.game.p1.spells:

		self.draw_string(translate(spell.name, "spell_name"), self.middle_menu_display, cur_x, cur_y, mouse_content=spell, content_width=col_width)
		cur_y += self.linesize

		# Upgrades
		for upgrade in sorted((b for b in self.game.p1.buffs if isinstance(b, RiftWizard.Upgrade) and b.prereq == spell), key=lambda b: b.shrine_name is None):
			fmt = translate(upgrade.name, "upgrade_name")
			if upgrade.shrine_name:
				color = RiftWizard.COLOR_XP
				fmt = upgrade.name.replace("(%s)" % spell.name, "")
			else:
				color = (255, 255, 255)
			self.draw_string(" " + fmt, self.middle_menu_display, cur_x, cur_y, mouse_content=upgrade, content_width=col_width, color=color)

			cur_y += self.linesize

		available_upgrades = len([b for b in spell.spell_upgrades if not b.applied])
		if available_upgrades and not self.game.spell_is_upgraded(spell):
			self.draw_string(" %d個のアップグレードから選択できる" % available_upgrades, self.middle_menu_display, cur_x, cur_y)
			cur_y += self.linesize

		spell_index += 1

	learn_color = (255, 255, 255) if len(self.game.p1.spells) < 20 else (170, 170, 170)

	self.draw_string("新しい呪文を習得する（Ｓ）", self.middle_menu_display, cur_x, cur_y, learn_color, mouse_content=RiftWizard.LEARN_SPELL_TARGET, content_width=col_width)

	# Skills
	skill_x_offset = self.middle_menu_display.get_width() // 2 + self.border_margin
	cur_x = skill_x_offset
	cur_y = self.linesize
	self.draw_string("スキル", self.middle_menu_display, cur_x, cur_y)

	cur_y += self.linesize
	cur_y += self.linesize

	for skill in self.game.p1.get_skills():
		self.draw_string(translate(skill.name, "skill_name"), self.middle_menu_display, cur_x, cur_y, mouse_content=skill, content_width=col_width)
		cur_y += self.linesize
	self.draw_string("新しいスキルを習得する（Ｋ）", self.middle_menu_display, cur_x, cur_y, mouse_content=RiftWizard.LEARN_SKILL_TARGET, content_width=col_width)

	cur_y += 4 * self.linesize

	#EQUIPMENT
	equipment = self.game.p1.get_equipment()

	if equipment:
		self.draw_string("装備：", self.middle_menu_display, cur_x, cur_y)
		cur_y += 2 * self.linesize

		for e in equipment:
			if e.name == "エキゾチック・ペット":
				self.draw_string(translate(e.spawn_fn().name, "monster_name"), self.middle_menu_display, cur_x, cur_y, mouse_content=e, content_width=col_width)
			else:
				self.draw_string(translate(e.name, "equipment_name"), self.middle_menu_display, cur_x, cur_y, mouse_content=e, content_width=col_width)
			cur_y += self.linesize

	self.screen.blit(self.middle_menu_display, (self.h_margin, 0))


RiftWizard.PyGameView.draw_char_sheet = draw_char_sheet


def draw_character(self):

	self.draw_panel(self.character_display)

	self.char_panel_examine_lines = {}

	cur_x = self.border_margin
	cur_y = self.border_margin
	linesize = self.linesize

	hpcolor = (255, 255, 255)
	if self.game.p1.cur_hp <= 25:
		hpcolor = (255, 0, 0)

	self.draw_string("%s %d/%d" % (RiftWizard.CHAR_HEART, self.game.p1.cur_hp, self.game.p1.max_hp), self.character_display, cur_x, cur_y, color=hpcolor)
	self.draw_string("%s" % RiftWizard.CHAR_HEART, self.character_display, cur_x, cur_y, (255, 0, 0))
	cur_y += linesize

	if self.game.p1.shields:
		self.draw_string("%s %d" % (RiftWizard.CHAR_SHIELD, self.game.p1.shields), self.character_display, cur_x, cur_y)
		self.draw_string("%s" % (RiftWizard.CHAR_SHIELD), self.character_display, cur_x, cur_y, color=RiftWizard.COLOR_SHIELD.to_tup())
		cur_y += linesize

	self.draw_string("SP %d" % self.game.p1.xp, self.character_display, cur_x, cur_y, color=RiftWizard.COLOR_XP)
	cur_y += linesize

	self.draw_string("レルム %d、ターン %d" % (self.game.level_num, self.game.cur_level.turn_no), self.character_display, cur_x, cur_y)
	cur_y += linesize

	# TODO- buffs here

	cur_y += linesize

	self.draw_string("呪文：", self.character_display, cur_x, cur_y)
	cur_y += linesize

	# Spells
	index = 1
	for spell in self.game.p1.spells:
		spell_number = (index) % 10
		mod_key = "C" if index > 20 else "S" if index > 10 else ""
		hotkey_str = "%s%d" % (mod_key, spell_number)

		if spell == self.cur_spell:
			cur_color = (0, 255, 0)
		elif spell.can_pay_costs():
			cur_color = (255, 255, 255)
		else:
			cur_color = (128, 128, 128)
		japanese_spell_name = translate(spell.name, "spell_name")
		fmt = "%-2s %-20s%2d" % (hotkey_str, japanese_spell_name, spell.cur_charges)
		if RiftWizard.SIZE == RiftWizard.SIZE_MED:
			fmt = "%-2s %-15s%2d" % (hotkey_str, japanese_spell_name, spell.cur_charges)
		if RiftWizard.SIZE == RiftWizard.SIZE_SMALL:
			fmt = "%s %-15s" % (hotkey_str, japanese_spell_name)

		self.draw_string(fmt, self.character_display, cur_x, cur_y, cur_color, mouse_content=RiftWizard.SpellCharacterWrapper(spell), char_panel=True)

		if RiftWizard.SIZE == RiftWizard.SIZE_MED:
			self.draw_spell_icon(spell, self.character_display, cur_x + 26, cur_y)
		elif RiftWizard.SIZE == RiftWizard.SIZE_SMALL:
			pass
		else:
			self.draw_spell_icon(spell, self.character_display, cur_x + 26, cur_y)

		cur_y += linesize
		index += 1

	cur_y += linesize
	# Items

	self.draw_string("アイテム:", self.character_display, cur_x, cur_y)
	cur_y += linesize
	index = 1
	for item in self.game.p1.items:

		hotkey_str = "%d" % (index % 10)

		cur_color = (255, 255, 255)
		if item.spell == self.cur_spell:
			cur_color = (0, 255, 0)

		japanese_item_name = translate(item.name, "item_name")
		fmt = "%s  %-20s%2d" % (hotkey_str, japanese_item_name, item.quantity)
		if RiftWizard.SIZE == RiftWizard.SIZE_MED:
			fmt = "%s  %-15s%2d" % (hotkey_str, japanese_item_name, item.quantity)
		if "size_small" in sys.argv:
			fmt = "%s %-13s%2d" % (hotkey_str, japanese_item_name, item.quantity)

		self.draw_string(fmt, self.character_display, cur_x, cur_y, cur_color, mouse_content=item)

		if "size_small" not in sys.argv:
			self.draw_spell_icon(item, self.character_display, cur_x + 26, cur_y)

		cur_y += linesize
		index += 1

	# Buffs
	status_effects = [b for b in self.game.p1.buffs if b.buff_type in [RiftWizard.BUFF_TYPE_BLESS, RiftWizard.BUFF_TYPE_CURSE]]
	counts = {}
	for effect in status_effects:
		if effect.name not in counts:
			counts[effect.name] = (effect, 0, 0, None)
		_, stacks, duration, color = counts[effect.name]
		stacks += 1
		duration = max(duration, effect.turns_left)

		counts[effect.name] = (effect, stacks, duration, effect.get_tooltip_color().to_tup())

	if status_effects:
		cur_y += linesize
		self.draw_string("状態:", self.character_display, cur_x, cur_y, (255, 255, 255))
		cur_y += linesize
		for buff_name, (buff, stacks, duration, color) in counts.items():

			fmt = translate(buff_name, "buff_name")

			if stacks > 1:
				fmt += "x%d" % stacks

			if duration:
				fmt += "（%d）" % duration

			self.draw_string(fmt, self.character_display, cur_x, cur_y, color, mouse_content=buff)
			cur_y += linesize

	surf_pos = self.get_surface_pos(self.character_display)
	if self.game.p1.equipment or self.game.p1.trinkets:
		cur_y += linesize
		self.draw_string("装備:", self.character_display, cur_x, cur_y, (255, 255, 255))
		cur_y += linesize

		item_list = []

		for slot in [RiftWizard.ITEM_SLOT_STAFF, RiftWizard.ITEM_SLOT_ROBE, RiftWizard.ITEM_SLOT_HEAD, RiftWizard.ITEM_SLOT_GLOVES, RiftWizard.ITEM_SLOT_BOOTS]:
			item = self.game.p1.equipment.get(slot)
			if item:
				item_list.append(item)

		item_list.extend(self.game.p1.trinkets)

		for item in item_list:

			abs_rect = RiftWizard.pygame.Rect(cur_x + surf_pos[0], cur_y + surf_pos[1], RiftWizard.SPRITE_SIZE, RiftWizard.SPRITE_SIZE)
			self.make_content_rect(self.character_display, abs_rect, item)

			icon = self.get_equipment_icon(item)
			self.character_display.blit(icon, (cur_x, cur_y))

			abs_rect = RiftWizard.pygame.Rect(cur_x + surf_pos[0], cur_y + surf_pos[1], RiftWizard.SPRITE_SIZE, RiftWizard.SPRITE_SIZE)

			cur_x += RiftWizard.SPRITE_SIZE + 2
			if cur_x > self.character_display.get_width() - self.border_margin - RiftWizard.SPRITE_SIZE:
				cur_x = self.border_margin
				cur_y += linesize

		cur_x = self.border_margin
		cur_y += linesize

	skills = [b for b in self.game.p1.buffs if b.buff_type == RiftWizard.BUFF_TYPE_PASSIVE and not b.prereq]
	if skills:
		cur_y += linesize

		self.draw_string("スキル:", self.character_display, cur_x, cur_y)
		cur_y += linesize

		skill_x_max = self.character_display.get_width() - self.border_margin - 16

		for skill in skills:

			abs_rect = RiftWizard.pygame.Rect(cur_x + surf_pos[0], cur_y + surf_pos[1], RiftWizard.SPRITE_SIZE, RiftWizard.SPRITE_SIZE)

			self.make_content_rect(self.character_display, abs_rect, skill)
			self.draw_spell_icon(skill, self.character_display, cur_x, cur_y)

			cur_x += RiftWizard.SPRITE_SIZE + 2
			if cur_x > self.character_display.get_width() - self.border_margin - RiftWizard.SPRITE_SIZE:
				cur_x = self.border_margin
				cur_y += linesize

		cur_y += linesize
		cur_x = self.border_margin

	resist_tags = [t for t in RiftWizard.Tags if t in self.game.p1.resists and self.game.p1.resists[t] != 0]
	resist_tags.sort(key=lambda t: -self.game.p1.resists[t])

	cur_y += self.linesize
	for negative in [False, True]:
		has_resists = False
		for tag in resist_tags:

			if not ((self.game.p1.resists[tag] < 0) == negative):
				continue

			self.draw_string("%d%% %s耐性" % (self.game.p1.resists[tag], translate(tag.name, "tag_name")), self.character_display, cur_x, cur_y, tag.color.to_tup())
			has_resists = True
			cur_y += self.linesize

		if has_resists:
			cur_y += self.linesize

	stunbuff = self.game.p1.get_buff(RiftWizard.Stun)
	if stunbuff:
		color = (255, 0, 0) if self.cast_fail_frames else stunbuff.color.to_tup()
		self.draw_string("%sで行動できない" % translate(stunbuff.name.upper(), "buff_name"), self.character_display, cur_x, cur_y, color=color, mouse_content=RiftWizard.STUNNED_TARGET)
		cur_y += linesize

	cur_x = self.border_margin
	cur_y = self.character_display.get_height() - self.border_margin - 4 * self.linesize

	if self.game.mutators:
		message = translate(self.game.trial_name, "trial_name")
		for mutator in self.game.mutators:
			message += "\n" + translate_lines(mutator.description, "trial_description")
		CHALLENGES_TARGET = RiftWizard.TooltipExamineTarget(message)
		self.draw_string(translate(self.game.trial_name, "trial_name"), self.character_display, cur_x, cur_y - self.linesize*2, mouse_content=CHALLENGES_TARGET)

	if RiftWizard.cheats_enabled:
		self.draw_string("チート有効", self.character_display, cur_x, cur_y - self.linesize, color=(255, 0, 0))

	if getattr(self.game, 'rift_rerolls', 0): # blocks a crash that came from trying to load a save that resulted in a crash
		if self.game.rift_rerolls == 1:
			self.draw_string("リフトをリロールする(R)", self.character_display, cur_x, cur_y, mouse_content=RiftWizard.REROLL_PORTALS_TARGET)
		else:
			self.draw_string("リフトをリロールする(R) (%d)" % self.game.rift_rerolls, self.character_display, cur_x, cur_y, mouse_content=RiftWizard.REROLL_PORTALS_TARGET)
	cur_y += linesize

	self.draw_string("メニュー(Esc)", self.character_display, cur_x, cur_y, mouse_content=RiftWizard.OPTIONS_TARGET)
	cur_y += linesize

	self.draw_string("プレイのしかた(H)", self.character_display, cur_x, cur_y, mouse_content=RiftWizard.INSTRUCTIONS_TARGET)
	cur_y += linesize

	color = self.game.p1.discount_tag.color.to_tup() if self.game.p1.discount_tag else (255, 255, 255)
	self.draw_string("キャラクターシート(C)", self.character_display, cur_x, cur_y, color=color, mouse_content=RiftWizard.CHAR_SHEET_TARGET)

	self.screen.blit(self.character_display, (0, 0))


RiftWizard.PyGameView.draw_character = draw_character


def draw_combat_log(self):
	cur_x = self.border_margin
	cur_y = self.border_margin

	self.middle_menu_display.fill((0, 0, 0))
	self.draw_panel(self.middle_menu_display)

	self.draw_string("レルム %d" % self.combat_log_level, self.middle_menu_display, cur_x, cur_y)
	cur_y += self.linesize
	if (self.game.is_awaiting_input() and self.game.p1.quick_cast_used):
		fmt = "ターン %d.5" % self.combat_log_turn
	else:
		fmt = "ターン %d" % self.combat_log_turn
		
	self.draw_string("ターン %d" % self.combat_log_turn, self.middle_menu_display, cur_x, cur_y)
	cur_y += self.linesize
	cur_y += self.linesize

	for line in self.combat_log_lines[1 + self.combat_log_offset :]:

		lines = self.draw_wrapped_string(line, self.middle_menu_display, cur_x, cur_y, self.middle_menu_display.get_width())
		cur_y += lines * self.linesize

		if cur_y + self.border_margin > self.middle_menu_display.get_height():
			break

	self.screen.blit(self.middle_menu_display, (self.h_margin, 0))


RiftWizard.PyGameView.draw_combat_log = draw_combat_log


def draw_examine_misc(self, target=None):
	border_margin = self.border_margin
	cur_x = border_margin
	cur_y = border_margin

	if not target:
		target = self.examine_target
	if hasattr(target, "name"):
		if isinstance(target, RiftWizard.Buff):
			name = translate(target.name, "buff_name")
		elif isinstance(target, RiftWizard.Item) or isinstance(target, RiftWizard.Prop):
			name = translate(target.name, "item_name")
		elif isinstance(target, RiftWizard.Cloud):
			name = translate(target.name, "cloud_name")
		else:
			name = target.name
		lines = self.draw_wrapped_string(name, self.examine_display, cur_x, cur_y, width=23 * 16)
		cur_y += (lines + 1) * self.linesize
	if hasattr(target, "get_description"):
		if isinstance(target, RiftWizard.Buff):
			description = translate_lines(target.get_description(), "buff_description")
		elif isinstance(target, RiftWizard.Item) or isinstance(target, RiftWizard.Prop):
			description = translate_lines(target.get_description(), "item_description")
		elif isinstance(target, RiftWizard.Cloud):
			description = translate_lines(target.get_description(), "cloud_description")
		else:
			description = target.get_description()
		self.draw_wrapped_string(description, self.examine_display, cur_x, cur_y, self.examine_display.get_width() - 2 * self.border_margin, extra_space=True)
	elif hasattr(target, "description"):
		if isinstance(target, RiftWizard.Buff):
			description = translate_lines(target.description, "buff_description")
		elif isinstance(target, RiftWizard.Item) or isinstance(target, RiftWizard.Prop):
			description = translate_lines(target.description, "item_description")
		elif isinstance(target, RiftWizard.Cloud):
			description = translate_lines(target.description, "cloud_description")
		else:
			description = target.description
		self.draw_wrapped_string(description, self.examine_display, cur_x, cur_y, self.examine_display.get_width() - 2 * self.border_margin, extra_space=True)


RiftWizard.PyGameView.draw_examine_misc = draw_examine_misc


def draw_examine_portal(self):

	border_margin = self.border_margin
	cur_x = border_margin
	cur_y = border_margin

	linesize = self.linesize

	gen_params = self.examine_target.level_gen_params

	self.draw_string("リフト", self.examine_display, cur_x, cur_y)
	cur_y += linesize

	if self.game.next_level or not self.game.has_granted_xp:
		cur_y += linesize
		self.draw_string("????????", self.examine_display, cur_x, cur_y)
		return

	if self.examine_target.locked:
		cur_y += linesize

		width = self.examine_display.get_width() - 2 * border_margin
		lines = self.draw_wrapped_string("（すべての敵を倒しすべてのゲートを破壊すると開く）", self.examine_display, cur_x, cur_y, width)
		cur_y += lines * linesize

	cur_y += linesize

	self.draw_string("内容：", self.examine_display, cur_x, cur_y)
	cur_y += 2 * linesize

	units = []

	COLOR_POP = (255, 255, 255)
	COLOR_BOSS = (253, 143, 77)
	COLOR_ELITE = COLOR_BOSS
	COLOR_ENC = (255, 0, 0)

	if gen_params.primary_spawn:
		unit = gen_params.primary_spawn()
		units.append((unit, COLOR_POP))

	if gen_params.secondary_spawn and gen_params.secondary_spawn != gen_params.primary_spawn:
		unit = gen_params.secondary_spawn()
		units.append((unit, COLOR_POP))

	drawn_bosses = set()
	for b in gen_params.bosses:
		if b.name in drawn_bosses:
			continue

		units.append((b, COLOR_BOSS if not b.is_boss else COLOR_ENC))
		drawn_bosses.add(b.name)

	for unit, color in units:

		sprite_sheet = self.get_sprite_sheet(RiftWizard.get_unit_asset(unit), radius=unit.radius, recolor_primary=unit.recolor_primary)
		frame = (RiftWizard.cloud_frame_clock // 12) % (len(sprite_sheet.anim_frames[RiftWizard.ANIM_IDLE]))

		if unit.outline_color:
			glow_image = sprite_sheet.get_glow_frame(RiftWizard.ANIM_IDLE, frame, unit.outline_color, flipped=False, outline=True)
			scaledimage = RiftWizard.pygame.transform.scale(glow_image, (36, 36))
			self.examine_display.blit(scaledimage, (cur_x - 2, cur_y - 2))

		sprite = sprite_sheet.anim_frames[RiftWizard.ANIM_IDLE][frame]
		scaledimage = RiftWizard.pygame.transform.scale(sprite, (32, 32))
		self.examine_display.blit(scaledimage, (cur_x, cur_y))

		name = translate(unit.name, "monster_name")
		if len(name) > 20:
			name = name[0:18] + ".."
		self.draw_string(name, self.examine_display, cur_x + 36, cur_y + 10, color)
		cur_y += 32 + 4

	cur_y += linesize

	width = self.examine_display.get_width() - 2 * border_margin

	for item in gen_params.items:
		image = RiftWizard.get_image(item.get_asset())

		frame = (RiftWizard.cloud_frame_clock // 12) % (image.get_width() // 16)
		sourcerect = (RiftWizard.SPRITE_SIZE * frame, 0, RiftWizard.SPRITE_SIZE, RiftWizard.SPRITE_SIZE)
		subimage = image.subsurface(sourcerect)
		scaledimage = RiftWizard.pygame.transform.scale(subimage, (32, 32))

		self.examine_display.blit(scaledimage, (cur_x, cur_y))
		self.draw_string(translate(item.name, "item_name"), self.examine_display, cur_x + 38, cur_y + 8)

		cur_y += 32

	for i in range(gen_params.num_xp):
		image = RiftWizard.get_image(["tiles", "items", "animated", "mana_orb"])

		frame = (RiftWizard.cloud_frame_clock // 12) % (image.get_width() // 16)
		sourcerect = (RiftWizard.SPRITE_SIZE * frame, 0, RiftWizard.SPRITE_SIZE, RiftWizard.SPRITE_SIZE)
		subimage = image.subsurface(sourcerect)
		scaledimage = RiftWizard.pygame.transform.scale(subimage, (32, 32))

		self.examine_display.blit(scaledimage, (cur_x, cur_y))
		self.draw_string("メモリー・オーブ", self.examine_display, cur_x + 38, cur_y + 8)
		cur_y += 32

	if gen_params.shrine:
		cur_y += linesize
		name = gen_params.shrine.name

		image = self.get_prop_image(gen_params.shrine)
		frame = (RiftWizard.cloud_frame_clock // 12) % (image.get_width() // 16)
		sourcerect = (RiftWizard.SPRITE_SIZE * frame, 0, RiftWizard.SPRITE_SIZE, RiftWizard.SPRITE_SIZE)
		subimage = image.subsurface(sourcerect)
		scaledimage = RiftWizard.pygame.transform.scale(subimage, (32, 32))

		self.examine_display.blit(scaledimage, (cur_x, cur_y))

		self.draw_string(translate(gen_params.shrine.name, "shrine_name"), self.examine_display, 38 + border_margin, cur_y + 8, content_width=width)

		cur_y += 32
		if isinstance(gen_params.shrine, RiftWizard.Shop):
			for item in gen_params.shrine.items:
				if isinstance(item, RiftWizard.Spell):
					japanese_name = translate(item.name, "spell_name")
				elif isinstance(item, RiftWizard.Upgrade):
					japanese_name = translate(item.name, "skill_name")
				else:
					japanese_name = translate(item.name, "equipment_name")
				self.draw_string(japanese_name, self.examine_display, cur_x + 38, cur_y)
				icon = self.get_equipment_icon(item)
				if icon:
					self.examine_display.blit(icon, (cur_x + 16, cur_y))
				cur_y += linesize


RiftWizard.PyGameView.draw_examine_portal = draw_examine_portal


def draw_examine_shop(self):
	cur_x = self.border_margin
	cur_y = self.border_margin

	self.draw_string(translate(self.examine_target.name, "shrine_name"), self.examine_display, cur_x, cur_y)
	cur_y += self.linesize

	image = self.get_prop_image(self.examine_target)
	frame = (RiftWizard.cloud_frame_clock // 12) % (image.get_width() // 16)
	sourcerect = (RiftWizard.SPRITE_SIZE * frame, 0, RiftWizard.SPRITE_SIZE, RiftWizard.SPRITE_SIZE)
	subimage = image.subsurface(sourcerect)
	scaledimage = RiftWizard.pygame.transform.scale(subimage, (64, 64))

	self.examine_display.blit(scaledimage, (self.examine_display.get_width() - self.border_margin - 64, 0))


	if not self.examine_target.items: # for shrines
		cur_y += self.linesize * 2
		desc_len = self.draw_wrapped_string(translate(self.examine_target.description, "shrine_description"), self.examine_display, cur_x, cur_y,
											width=self.examine_display.get_width() - cur_x - self.border_margin)
		cur_y += self.linesize * desc_len

	for item in self.examine_target.items:
		if isinstance(item, RiftWizard.Spell):
			japanese_name = translate(item.name, "spell_name")
		elif isinstance(item, RiftWizard.Equipment):
			japanese_name = translate(item.name, "equipment_name")
		elif isinstance(item, RiftWizard.Upgrade):
			japanese_name = translate(item.name, "skill_name")
		else:
			japanese_name = translate(item.name, "item_name")
		self.draw_string(japanese_name, self.examine_display, cur_x + 38, cur_y)
		icon = self.get_equipment_icon(item)
		if icon:
			self.examine_display.blit(icon, (cur_x + 16, cur_y))
		cur_y += self.linesize


RiftWizard.PyGameView.draw_examine_shop = draw_examine_shop


def draw_examine_spell(self):

	self.draw_examine_icon()

	border_margin = self.border_margin
	cur_x = border_margin
	cur_y = border_margin
	linesize = self.linesize

	spell = self.examine_target
	self.draw_string(translate(spell.name, "spell_name"), self.examine_display, cur_x, cur_y)
	cur_y += linesize
	cur_y += linesize
	tag_x = cur_x
	for tag in RiftWizard.Tags:
		if tag not in spell.tags:
			continue
		self.draw_string(translate(tag.name, "tag_name"), self.examine_display, tag_x, cur_y, (tag.color.r, tag.color.g, tag.color.b))
		cur_y += linesize
	cur_y += linesize

	if spell.level:
		self.draw_string("レベル %d" % spell.level, self.examine_display, cur_x, cur_y)
		cur_y += linesize

	if spell.melee:
		self.draw_string("近接", self.examine_display, cur_x, cur_y)
		cur_y += self.linesize
	elif spell.range:
		fmt = "射程 %d" % spell.get_stat("range")
		if not spell.requires_los:
			fmt += "（視線不要）"
		self.draw_string(fmt, self.examine_display, cur_x, cur_y)
		cur_y += self.linesize

	if spell.get_stat('quick_cast'):
		self.draw_string("高速詠唱", self.examine_display, cur_x, cur_y)
		cur_y += self.linesize

	if spell.max_charges:
		self.draw_string("チャージ：%d/%d " % (self.examine_target.cur_charges, self.examine_target.get_stat("max_charges")), self.examine_display, cur_x, cur_y)
		cur_y += self.linesize

	if spell.hp_cost:
		self.draw_string("HPコスト：%d" % spell.get_stat("hp_cost"), self.examine_display, cur_x, cur_y)
		cur_y += self.linesize

	cur_y += linesize

	lines = self.draw_wrapped_string(translate_lines(spell.get_description(), "spell_description"), self.examine_display, cur_x, cur_y, self.examine_display.get_width() - 2 * self.border_margin, extra_space=True)
	cur_y += linesize * lines

	if RiftWizard.SIZE == RiftWizard.SIZE_LARGE:
		self.draw_string("効果：", self.examine_display, cur_x, cur_y)
		cur_y += self.linesize
		had_attrs = False

		for attr in RiftWizard.tt_attrs:
			if not getattr(self.examine_target, attr, None): # don't display 0 attributes
				continue
			had_attrs = True
			self.draw_string(" %3d %s" % (self.examine_target.get_stat(attr), translate(RiftWizard.format_attr(attr), "attr_name")), self.examine_display, cur_x, cur_y, RiftWizard.attr_colors[attr].to_tup())
			cur_y += self.linesize

		if not had_attrs:
			self.draw_string(" なし", self.examine_display, cur_x, cur_y)
			cur_y += self.linesize
		cur_y += self.linesize

	if spell.spell_upgrades:
		self.draw_string("アップグレード：", self.examine_display, cur_x, cur_y)
		cur_y += linesize

		for upg in spell.spell_upgrades:

			cur_color = (255, 255, 255)
			if self.game.has_upgrade(upg):
				cur_color = (0, 255, 0)

			self.draw_string(" %d：%s" % (upg.level, translate(upg.name, "upgrade_name")), self.examine_display, cur_x, cur_y, color=cur_color)
			cur_y += linesize


RiftWizard.PyGameView.draw_examine_spell = draw_examine_spell


def draw_examine_unit(self):
	# If a game is running, do not display dead monsters or the player
	if self.game:
		if self.examine_target.killed:
			return

		if self.examine_target == self.game.p1:
			return

	if self.state == RiftWizard.STATE_SHOP and self.shop_type == RiftWizard.SHOP_TYPE_BESTIARY:
		if not RiftWizard.SteamAdapter.has_slain(self.examine_target.name):
			return

	border_margin = self.border_margin
	cur_x = border_margin
	cur_y = border_margin
	linesize = self.linesize
	unit = self.examine_target

	self.unit_examine_icon_surface.fill((0, 0, 0))

	if not self.examine_target.Anim:
		self.examine_target.Anim = self.get_anim(self.examine_target)

	if self.examine_target.Anim:
		self.examine_target.Anim.draw(self.unit_examine_icon_surface, True)

	icon_size = 64 * 5
	if RiftWizard.SIZE == RiftWizard.SIZE_SMALL:
		icon_size = 32 * 5

	panel_subsurface = self.examine_display.subsurface((self.examine_display.get_width() - self.border_margin - icon_size, self.border_margin, icon_size, icon_size))

	RiftWizard.pygame.transform.scale(self.unit_examine_icon_surface, (icon_size, icon_size), panel_subsurface)

	lines = self.draw_wrapped_string(translate(unit.name, "monster_name"), self.examine_display, cur_x, cur_y, width=17 * 16)
	cur_y += (lines + 1) * linesize

	if unit.team == RiftWizard.TEAM_PLAYER:
		self.draw_string("友好的", self.examine_display, cur_x, cur_y, RiftWizard.Tags.Conjuration.color.to_tup())
		cur_y += linesize

	if unit.turns_to_death:
		self.draw_string("残り%dターン" % unit.turns_to_death, self.examine_display, cur_x, cur_y)
		cur_y += linesize

	if unit.cur_hp > 0:
		self.draw_string("%s %d/%d" % (RiftWizard.CHAR_HEART, unit.cur_hp, unit.max_hp), self.examine_display, cur_x, cur_y)
		self.draw_string("%s" % RiftWizard.CHAR_HEART, self.examine_display, cur_x, cur_y, (255, 0, 0))
	else:
		self.draw_string("%d HP" % unit.max_hp, self.examine_display, cur_x, cur_y, RiftWizard.attr_colors["minion_health"].to_tup())
	cur_y += linesize
	if unit.shields:
		self.draw_string("%s %d" % (RiftWizard.CHAR_SHIELD, unit.shields), self.examine_display, cur_x, cur_y)
		self.draw_string("%s" % (RiftWizard.CHAR_SHIELD), self.examine_display, cur_x, cur_y, color=RiftWizard.COLOR_SHIELD.to_tup())
		cur_y += linesize

	if unit.clarity:
		self.draw_string("%s %d" % (RiftWizard.CHAR_CLARITY, unit.clarity), self.examine_display, cur_x, cur_y)
		self.draw_string("%s" % (RiftWizard.CHAR_CLARITY), self.examine_display, cur_x, cur_y, color=RiftWizard.COLOR_CLARITY)
		cur_y += linesize

	cur_y += linesize
	for tag in unit.tags:
		self.draw_string(translate(tag.name, "tag_name"), self.examine_display, cur_x, cur_y, (tag.color.r, tag.color.g, tag.color.b))
		cur_y += linesize

	cur_y += linesize
	for spell in unit.spells:
		if hasattr(spell, "damage_type") and isinstance(spell.damage_type, RiftWizard.Tag):
			cur_color = spell.damage_type.color.to_tup()
		else:
			cur_color = (255, 255, 255)

		fmt = "%s" % translate(spell.name, "monster_spell_name")
		lines = self.draw_wrapped_string(fmt, self.examine_display, cur_x, cur_y, self.examine_display.get_width() - (2 * border_margin), cur_color)
		cur_y += lines * linesize
		hasattrs = False
		if hasattr(spell, "damage"):
			if hasattr(spell, "damage_type") and isinstance(spell.damage_type, RiftWizard.Tag):
				fmt = " %d%sダメージ" % (spell.get_stat("damage"), translate(spell.damage_type.name, "tag_name"))
			elif hasattr(spell, "damage_type") and isinstance(spell.damage_type, list):
				connector = 'または' if getattr(spell, 'damage_type_random', False) else 'と'
				fmt = " %d%sダメージ" % (spell.damage, connector.join([translate(t.name, "tag_name") for t in spell.damage_type]))
			else:
				fmt = " %dダメージ" % spell.get_stat("damage")
			lines = self.draw_wrapped_string(fmt, self.examine_display, cur_x, cur_y, self.examine_display.get_width() - 2 * border_margin, color=RiftWizard.COLOR_DAMAGE.to_tup())
			cur_y += lines * linesize
			hasattrs = True
		if spell.range > 1.5:
			fmt = " 射程%d" % spell.get_stat("range")
			self.draw_string(fmt, self.examine_display, cur_x, cur_y, RiftWizard.COLOR_RANGE.to_tup())
			cur_y += linesize
			hasattrs = True
		if hasattr(spell, "radius") and spell.get_stat("radius") > 0:
			fmt = " 範囲%d" % spell.radius
			self.draw_string(fmt, self.examine_display, cur_x, cur_y, RiftWizard.attr_colors["radius"].to_tup())
			cur_y += linesize
			hasattrs = True
		if hasattr(spell, 'hp_cost') and spell.get_stat('hp_cost') > 0:
			fmt = ' %d HPコスト' % spell.get_stat('hp_cost')
			self.draw_string(fmt, self.examine_display, cur_x, cur_y, RiftWizard.Tags.Blood.color.to_tup())
			cur_y += self.linesize
			hasattrs = True
		if spell.get_stat('cool_down') > 0 or spell.cool_down > 0:
			cd = 0
			if spell.statholder and spell.statholder != spell.owner: # for spells granted by the wizard where the wizard is the statholder
				cd = spell.cool_down
			else: # for spells the creature has innately
				cd = spell.get_stat('cool_down')
			rem_cd = 0
			if spell.caster:
				rem_cd = spell.caster.cool_downs.get(spell, 0)

			if not rem_cd:
				fmt = " クールダウン%dターン" % cd
			else:
				fmt = " クールダウン%dターン（%d）" % (cd, rem_cd)
			self.draw_string(fmt, self.examine_display, cur_x, cur_y)
			cur_y += linesize
			hasattrs = True

		# Prioritize spell.description so it can be overriden
		desc = spell.description or spell.get_description()
		if desc:
			indent = 16
			lines = self.draw_wrapped_string(translate_lines(desc, "monster_spell_description"), self.examine_display, cur_x + 16, cur_y, self.examine_display.get_width() - (indent + 2 * border_margin))
			cur_y += lines * linesize
		cur_y += linesize

	if unit.flying:
		self.draw_string("飛行", self.examine_display, cur_x, cur_y)
		cur_y += linesize

	if unit.stationary:
		self.draw_string("移動不可", self.examine_display, cur_x, cur_y)
		cur_y += linesize

	if unit.burrowing:
		self.draw_string("掘削", self.examine_display, cur_x, cur_y)
		cur_y += linesize

	if unit.flying or unit.stationary or unit.burrowing:
		cur_y += linesize

	resist_tags = [t for t in RiftWizard.Tags if t in self.examine_target.resists and self.examine_target.resists[t] != 0]
	resist_tags.sort(key=lambda t: -self.examine_target.resists[t])

	for negative in [False, True]:
		has_resists = False
		for tag in resist_tags:
			if not ((self.examine_target.resists[tag] < 0) == negative):
				continue

			self.draw_string("%d%% %s耐性" % (self.examine_target.resists[tag], translate(tag.name, "tag_name")), self.examine_display, cur_x, cur_y, tag.color.to_tup())
			has_resists = True
			cur_y += self.linesize

		if has_resists:
			cur_y += self.linesize

	# Unit Passives
	if hasattr(self.examine_target, "level"):
		passives = [b for b in self.examine_target.buffs if b.buff_type == RiftWizard.BUFF_TYPE_PASSIVE]
	else:
		passives = self.examine_target.buffs

	for buff in passives:

		buff_desc = buff.get_tooltip()
		if not buff_desc:
			continue

		buff_color = buff.get_tooltip_color()
		if not buff_color:
			buff_color = RiftWizard.Color(255, 255, 255)
		buff_color = (buff_color.r, buff_color.g, buff_color.b)

		lines = self.draw_wrapped_string(translate_lines(buff_desc, "buff_description"), self.examine_display, cur_x, cur_y, self.examine_display.get_width() - 2 * border_margin, buff_color)
		cur_y += linesize * (lines + 1)

	cur_y += linesize

	if hasattr(self.examine_target, "level"):
		status_effects = [b for b in self.examine_target.buffs if b.buff_type in [RiftWizard.BUFF_TYPE_BLESS, RiftWizard.BUFF_TYPE_CURSE]]
	else:
		status_effects = []

	counts = {}
	for effect in status_effects:
		if effect.name not in counts:
			counts[effect.name] = (effect, 0, 0, None)
		_, stacks, duration, color = counts[effect.name]
		stacks += 1
		duration = max(duration, effect.turns_left)

		counts[effect.name] = (effect, stacks, duration, effect.get_tooltip_color().to_tup())

	if status_effects:
		cur_y += linesize
		self.draw_string("状態：", self.examine_display, cur_x, cur_y, (255, 255, 255))
		cur_y += linesize
		for buff_name, (buff, stacks, duration, color) in counts.items():

			fmt = translate(buff_name, "buff_name")

			if stacks > 1:
				fmt += "x%d" % stacks

			if duration:
				fmt += "（%d）" % duration

			self.draw_string(fmt, self.examine_display, cur_x, cur_y, color, mouse_content=buff)
			cur_y += linesize


RiftWizard.PyGameView.draw_examine_unit = draw_examine_unit


def draw_examine_upgrade(self):
	path = ["UI", "spell skill icons", self.examine_target.name.lower().replace(" ", "_") + ".png"]
	self.draw_examine_icon()

	border_margin = self.border_margin
	cur_x = border_margin
	cur_y = border_margin

	if isinstance(self.examine_target, RiftWizard.Equipment):
		japanese_name = translate(self.examine_target.name, "equipment_name")
	elif isinstance(self.examine_target, RiftWizard.SpellUpgrade) or self.examine_target.prereq is not None:
		japanese_name = translate(self.examine_target.name, "upgrade_name")
	elif isinstance(self.examine_target, RiftWizard.Upgrade):
		japanese_name = translate(self.examine_target.name, "skill_name")
	else:
		japanese_name = translate(self.examine_target.name, "buff_name")
	width = self.examine_display.get_width() - 2 * border_margin
	lines = self.draw_wrapped_string(japanese_name, self.examine_display, cur_x, cur_y, width=width)
	cur_y += self.linesize * lines

	# For items, draw item type
	if isinstance(self.examine_target, RiftWizard.Equipment):
		if self.examine_target.slot == RiftWizard.ITEM_SLOT_AMULET:
			slot_str = "トリンケット"
		elif self.examine_target.slot == RiftWizard.ITEM_SLOT_STAFF:
			slot_str = "スタッフ"
		elif self.examine_target.slot == RiftWizard.ITEM_SLOT_HEAD:
			slot_str = "ヘルメット"
		elif self.examine_target.slot == RiftWizard.ITEM_SLOT_ROBE:
			slot_str = "ローブ"
		elif self.examine_target.slot == RiftWizard.ITEM_SLOT_BOOTS:
			slot_str = "ブーツ"

		self.draw_string(slot_str, self.examine_display, cur_x, cur_y)
		cur_y += self.linesize

	cur_y += self.linesize

	# Draw upgrade tags
	if not getattr(self.examine_target, "prereq", None) and hasattr(self.examine_target, "tags"):
		for tag in RiftWizard.Tags:
			if tag not in self.examine_target.tags:
				continue
			self.draw_string(translate(tag.name, "tag_name"), self.examine_display, cur_x, cur_y, (tag.color.r, tag.color.g, tag.color.b))
			cur_y += self.linesize
		cur_y += self.linesize

	if getattr(self.examine_target, "level", None):
		self.draw_string("レベル %d" % self.examine_target.level, self.examine_display, cur_x, cur_y)
		cur_y += self.linesize

	cur_y += self.linesize

	is_passive = isinstance(self.examine_target, RiftWizard.Upgrade) and not self.examine_target.prereq

	# Autogen boring part of description

	for tag, bonuses in self.examine_target.tag_bonuses_pct.items():
		for attr, val in bonuses.items():
			fmt = "%sの呪文とスキルは[%d%%%s:%s]を得る。" % (translate(tag.name, "tag_name"), int(val), translate(RiftWizard.format_attr(attr), "attr_name"), attr)
			lines = self.draw_wrapped_string(fmt, self.examine_display, cur_x, cur_y, width=width)
			cur_y += (lines + 1) * self.linesize

	for tag, bonuses in self.examine_target.tag_bonuses.items():
		for attr, val in bonuses.items():
			fmt = "%sの呪文とスキルは[%s%s:%s]を得る。" % (translate(tag.name, "tag_name"), val, translate(RiftWizard.format_attr(attr), "attr_name"), attr)
			lines = self.draw_wrapped_string(fmt, self.examine_display, cur_x, cur_y, width=width)
			cur_y += (lines + 1) * self.linesize

	for spell, bonuses in self.examine_target.spell_bonuses_pct.items():
		spell_ex = spell()

		useful_bonuses = [(attr, val) for (attr, val) in bonuses.items() if hasattr(spell_ex, attr)]
		if not useful_bonuses:
			continue

		for attr, val in useful_bonuses:
			if attr in RiftWizard.tooltip_colors:
				fmt = "%sは[%s%%%s:%s]を得る" % (translate(spell_ex.name, "spell_name"), val, translate(RiftWizard.format_attr(attr), "attr_name"), attr)
			else:
				fmt = "%sは%d%sを得る" % (translate(spell_ex.name, "spell_name"), val, translate(RiftWizard.format_attr(attr), "attr_name"))
			lines = self.draw_wrapped_string(fmt, self.examine_display, cur_x, cur_y, width=width)
			cur_y += (lines + 1) * self.linesize

	for spell, bonuses in self.examine_target.spell_bonuses.items():
		spell_ex = spell()

		useful_bonuses = [(attr, val) for (attr, val) in bonuses.items() if hasattr(spell_ex, attr)]
		if not useful_bonuses:
			continue

		for attr, val in useful_bonuses:
			if attr in RiftWizard.tooltip_colors:
				fmt = "%sは[%s%s:%s]を得る" % (translate(spell_ex.name, "spell_name"), val, translate(RiftWizard.format_attr(attr), "attr_name"), attr)
			else:
				fmt = "%sは%d%sを得る" % (translate(spell_ex.name, "spell_name"), val, translate(RiftWizard.format_attr(attr), "attr_name"))
			lines = self.draw_wrapped_string(fmt, self.examine_display, cur_x, cur_y, width=width)
			cur_y += (lines + 1) * self.linesize

	if hasattr(self.examine_target, 'new_attributes') and hasattr(self.examine_target, 'prereq'):
		spell = self.examine_target.prereq.name
		for attr, val in self.examine_target.new_attributes.items():
			if attr in RiftWizard.tt_attrs or attr == 'hp_cost':
				fmt = "%sは[%s%s:%s]を得る。" % (translate(spell, "spell_name"), val, translate(attr, "attr_name"), attr)
			else:
				continue
			lines = self.draw_wrapped_string(fmt, self.examine_display, cur_x, cur_y, width=width)
			cur_y += (lines+1) * self.linesize

	for attr, val in self.examine_target.global_bonuses_pct.items():
		if val >= 0:
			fmt = "すべての呪文とスキルは[%d%%%s:%s]を得る" % (int(val), translate(attr, "attr_name"),attr)
		else:
			fmt = "すべての呪文とスキルは[%d%%%s:%s]を失う" % (int(val), translate(attr, "attr_name"),attr)
		lines = self.draw_wrapped_string(fmt, self.examine_display, cur_x, cur_y, width)
		cur_y += (lines + 1) * self.linesize

	for attr, val in self.examine_target.global_bonuses.items():
		if val >= 0:
			fmt = "すべての呪文とスキルは[%d%s:%s]を得る" % (int(val), translate(attr, "attr_name"),attr)
		else:
			fmt = "すべての呪文とスキルは[%d%s:%s]を失う" % (int(val), translate(attr, "attr_name"),attr)
		lines = self.draw_wrapped_string(fmt, self.examine_display, cur_x, cur_y, width)
		cur_y += (lines + 1) * self.linesize

	has_resists = False
	for tag in RiftWizard.Tags:
		if tag not in self.examine_target.resists:
			continue
		self.draw_string("%d%%　%s耐性" % (self.examine_target.resists[tag], translate(tag.name, "tag_name")), self.examine_display, cur_x, cur_y, tag.color.to_tup())
		has_resists = True
		cur_y += self.linesize

	if has_resists:
		cur_y += self.linesize
	if isinstance(self.examine_target, RiftWizard.Equipment):
		desc = translate_lines(self.examine_target.get_description(), "equipment_description")
	elif isinstance(self.examine_target, RiftWizard.SpellUpgrade) or self.examine_target.prereq is not None:
		desc = translate_lines(self.examine_target.get_description(), "upgrade_description")
	elif isinstance(self.examine_target, RiftWizard.Upgrade):
		desc = translate_lines(self.examine_target.get_description(), "skill_description")
	else:
		desc = translate_lines(self.examine_target.get_description(), "buff_description")
	if not desc:
		if isinstance(self.examine_target, RiftWizard.Equipment):
			desc = translate_lines(self.examine_target.get_tooltip(), "equipment_description")
		elif isinstance(self.examine_target, RiftWizard.SpellUpgrade) or self.examine_target.prereq is not None:
			desc = translate_lines(self.examine_target.get_tooltip(), "upgrade_description")
		elif isinstance(self.examine_target, RiftWizard.Upgrade):
			desc = translate_lines(self.examine_target.get_tooltip(), "upgrade_description")
		else:
			desc = translate_lines(self.examine_target.get_tooltip(), "buff_description")

	# Warn player about replacing shrine buffs
	if getattr(self.examine_target, "shrine_name", None):
		existing = [b for b in self.game.p1.buffs if isinstance(b, RiftWizard.Upgrade) and b.prereq == self.examine_target.prereq and b.shrine_name and b != self.examine_target]
		if existing:
			if not desc:
				desc = ""
			desc += "\n警告：%sと交換されます" % existing[0].name

	if desc:
		lines = self.draw_wrapped_string(desc, self.examine_display, cur_x, cur_y, width, extra_space=True)
		cur_y += lines * self.linesize

	if RiftWizard.SIZE == RiftWizard.SIZE_LARGE and isinstance(self.examine_target, RiftWizard.Upgrade) and not self.examine_target.prereq:
		self.draw_string("効果：", self.examine_display, cur_x, cur_y)
		cur_y += self.linesize
		had_attrs = False

		for attr in RiftWizard.tt_attrs:
			if not hasattr(self.examine_target, attr):
				continue
			had_attrs = True
			self.draw_string(" %3d %s" % (self.examine_target.get_stat(attr), translate(RiftWizard.format_attr(attr), "attr_name")), self.examine_display, cur_x, cur_y, RiftWizard.attr_colors[attr].to_tup())
			cur_y += self.linesize

		if not had_attrs:
			self.draw_string(" なし", self.examine_display, cur_x, cur_y)
			cur_y += self.linesize
		cur_y += self.linesize

	# Inform player if this item will replace a currently held one
	if isinstance(self.examine_target, RiftWizard.Equipment):
		if self.examine_target.slot != RiftWizard.ITEM_SLOT_AMULET and not self.examine_target.applied and self.game.p1.equipment.get(self.examine_target.slot):
			self.draw_wrapped_string("（%sと交換されます）" % translate(self.game.p1.equipment[self.examine_target.slot].name, "equipment_name"), self.examine_display, cur_x, cur_y, width)


RiftWizard.PyGameView.draw_examine_upgrade = draw_examine_upgrade


def draw_pick_mode(self):
	opts = [("通常のゲーム", RiftWizard.GAME_MODE_NORMAL),
			("大魔術師の試練", RiftWizard.GAME_MODE_TRIALS),
			("今週の挑戦", RiftWizard.GAME_MODE_WEEKLY),
			("変異した挑戦", RiftWizard.GAME_MODE_RANDOM),
			("カスタムした挑戦", RiftWizard.GAME_MODE_CUSTOM)]

	rect_w = self.font.size("カスタムした挑戦")[0]
	cur_x = self.screen.get_width() // 2 - (self.font.size("カスタムした挑戦")[0] // 2)
	cur_y = self.screen.get_height() // 2 - self.linesize * 4

	cur_color = (255, 255, 255)
	for t, o in opts:

		cur_color = (255, 255, 255)

		self.draw_string(t, self.screen, cur_x, cur_y, cur_color, mouse_content=o, content_width=rect_w)
		if ((o == RiftWizard.GAME_MODE_NORMAL and RiftWizard.SteamAdapter.get_stat('w')) or
			(o == RiftWizard.GAME_MODE_WEEKLY and RiftWizard.SteamAdapter.get_trial_status(RiftWizard.get_weekly_name())) or
			(o == RiftWizard.GAME_MODE_TRIALS and all(RiftWizard.SteamAdapter.get_trial_status(t.name) for t in RiftWizard.all_trials))):
			self.draw_string("*", self.screen, cur_x - 16, cur_y, RiftWizard.COLOR_VICTORY)

		cur_y += self.linesize

RiftWizard.PyGameView.draw_pick_mode = draw_pick_mode


def draw_pick_trial(self):

	rect_w = max(self.font.size(translate(trial.name, "trial_name"))[0] for trial in RiftWizard.all_trials)
	cur_x = self.screen.get_width() // 2 - rect_w // 2
	cur_y = self.screen.get_height() // 2 - self.linesize * 8

	cur_color = (255, 255, 255)
	for trial in RiftWizard.all_trials:
		self.draw_string(translate(trial.name, "trial_name"), self.screen, cur_x, cur_y, cur_color, mouse_content=trial, content_width=rect_w)
		if RiftWizard.SteamAdapter.get_trial_status(trial.name):
			self.draw_string("*", self.screen, cur_x - 16, cur_y, RiftWizard.COLOR_VICTORY)
		cur_y += self.linesize

	cur_y += self.linesize * 10

	if isinstance(self.examine_target, RiftWizard.Trial):
		desc = translate_lines(self.examine_target.get_description(), "trial_description")
		for line in desc.split("\n"):
			cur_x = (self.screen.get_width() // 2) - (self.font.size(line)[0] // 2)
			self.draw_string(line, self.screen, cur_x, cur_y)
			cur_y += self.linesize

RiftWizard.PyGameView.draw_pick_trial = draw_pick_trial


def draw_setup_custom(self):
	self.ui_rects = []
	col_w = self.screen.get_width() // 5
	line_height = self.linesize

	# Draw all mutators (column 2)
	x_all = col_w
	y = self.linesize * 4
	for mut in RiftWizard.all_mutators:
		name = mut.name if not isinstance(mut, type) else mut.__name__
		name = translate(name, "custom_name")

		w = self.font.size(name)[0]
		x = x_all
		self.draw_string(name, self.screen, x, y, (255, 255, 255), mouse_content=mut, content_width=w)
		self.ui_rects.append((RiftWizard.pygame.Rect(x, y, w, line_height), mut))
		y += line_height

	# Draw Play Button (column 3)
	x_play = col_w * 2 + col_w // 2
	label = "プレイ"
	label_w = self.font.size(label)[0]
	x = x_play - label_w // 2
	y = self.screen.get_height() - line_height * 4

	self.draw_string(label, self.screen, x, y, (255, 255, 255), mouse_content="play")
	self.ui_rects.append((RiftWizard.pygame.Rect(x, y, label_w, self.linesize), "play"))

	# Draw configured mutators (column 4)
	x_custom = col_w * 4
	y = self.linesize * 4

	for mut, args in zip(self.custom_mutators, self.custom_mutator_args):
		arg_strs = [translate(self.format_param_value(arg),"custom_param") for arg in args]
		translated_name = translate(mut.__class__.__name__, "custom_name")
		name = f"{translated_name}" + "".join("（"+s+"）" for s in arg_strs)

		w = self.font.size(name)[0]
		x = x_custom - w
		self.draw_string(name, self.screen, x, y, (255, 255, 255), mouse_content=mut, content_width=w)
		self.ui_rects.append((RiftWizard.pygame.Rect(x, y, w, line_height), mut))
		y += line_height

	# Draw description (center column)
	if self.examine_target in self.custom_mutators or self.examine_target in RiftWizard.all_mutators:
		if self.examine_target in self.custom_mutators:
			desc_lines = getattr(self.examine_target, 'description', '').split('\n')
		else:
			desc_lines = self.get_placeholder_description(self.examine_target).split('\n')

		if RiftWizard.SIZE == RiftWizard.SIZE_SMALL:
			y = self.screen.get_height() // 2
		else:
			y = self.screen.get_height() - line_height * 8

		for line in desc_lines:
			line = translate(line, "trial_description")
			if RiftWizard.SIZE == RiftWizard.SIZE_SMALL:
				x = col_w * 2
				num_lines = self.draw_wrapped_string(line, self.screen, x, y, col_w, indent=False, center=True)
				y += line_height * (num_lines + 1)
			else:
				x = (self.screen.get_width() // 2) - (self.font.size(line)[0] // 2)
				self.draw_string(line, self.screen, x, y)
				y += line_height

RiftWizard.PyGameView.draw_setup_custom = draw_setup_custom

def get_placeholder_description(self, mutator_class):
	# MEMO: このメソッドのために、変数を持つMutatorsについてはJapanese.pyで placeholder_description を独自定義している
	temp_instance = self.create_placeholder_instance(mutator_class)
	if mutator_class in RiftWizard.mutators_with_no_args:
		return getattr(temp_instance, "description", "No Description")

	raw_description = getattr(temp_instance, "description", "")

	if mutator_class in RiftWizard.mutators_with_vals or mutator_class in RiftWizard.mutators_with_params_and_vals:
		dummy_val = 25
		if str(dummy_val) in raw_description:
			raw_description = raw_description.replace(str(dummy_val), 'X')

	if mutator_class in RiftWizard.mutators_with_params:
		return getattr(temp_instance, "placeholder_description", "No Description")

	return raw_description

RiftWizard.PyGameView.get_placeholder_description = get_placeholder_description


def draw_pick_mutator_params(self):
	self.ui_rects = []
	center_x = self.screen.get_width() // 2
	options = RiftWizard.mutator_param_options.get(self.pending_mutator_class, [])

	if options:
		if len(options) > 20:
			# Multi-column layout for lots of options
			cur_y = self.screen.get_height() // 20
			cols = 5
			col_width = self.screen.get_width() // cols
			max_rows = (self.screen.get_height() - cur_y - self.linesize) // self.linesize
			per_col = max_rows

			start_y = cur_y
			for idx, opt in enumerate(options):
				col = idx // per_col
				row = idx % per_col
				if col >= cols:
					break

				x = col * col_width + col_width // 2
				y = start_y + row * self.linesize

				label = self.format_param_value(opt)
				label = translate(label, "custom_param")
				label_w = self.font.size(label)[0]
				self.draw_string(label, self.screen, x - label_w // 2, y, (255, 255, 255), mouse_content=opt)
				self.ui_rects.append((RiftWizard.pygame.Rect(x - label_w // 2, y, label_w, self.linesize), opt))

		else:
			# Center vertically
			total_height = len(options) * self.linesize
			start_y = (self.screen.get_height() - total_height) // 4
			rect_w = max(self.font.size(self.format_param_value(opt))[0] for opt in options)
			cur_x = center_x - rect_w // 2

			# Mutator Name
			mut_name = self.pending_mutator_class.__name__
			mut_name = translate(mut_name, "custom_name")
			title_x = center_x - self.font.size(mut_name)[0] // 2
			self.draw_string(mut_name, self.screen, title_x, start_y, (255, 255, 255))
			start_y += self.linesize

			# Mutator Dummy Description
			desc_lines = self.get_placeholder_description(self.pending_mutator_class).split('\n')
			for line in desc_lines:
				line = translate(line, "trial_description")
				line_w = self.font.size(line)[0]
				line_x = center_x - line_w // 2
				self.draw_string(line, self.screen, line_x, start_y, (255, 255, 255))
				start_y += self.linesize

			start_y += self.linesize * 3

			for opt in options:
				label = self.format_param_value(opt)
				label = translate(label, "custom_param")
				label_w = self.font.size(label)[0]
				self.draw_string(label, self.screen, cur_x, start_y, (255, 255, 255), mouse_content=opt, content_width=rect_w)
				self.ui_rects.append((RiftWizard.pygame.Rect(cur_x, start_y, label_w, self.linesize), opt))
				start_y += self.linesize

RiftWizard.PyGameView.draw_pick_mutator_params = draw_pick_mutator_params

def draw_enter_mutator_value(self):
	self.ui_rects = []

	center_x = self.screen.get_width() // 2
	start_y = self.screen.get_height() // 4

	# Mutator Name
	mut_name = self.pending_mutator_class.__name__
	mut_name = translate(mut_name, "custom_name")
	title_x = center_x - self.font.size(mut_name)[0] // 2
	self.draw_string(mut_name, self.screen, title_x, start_y, (255, 255, 255))
	start_y += self.linesize

	#Mutator Dummy Description
	desc_lines = self.get_placeholder_description(self.pending_mutator_class).split('\n')
	for line in desc_lines:
		line = translate(line, "trial_description")
		line_w = self.font.size(line)[0]
		line_x = center_x - line_w // 2
		self.draw_string(line, self.screen, line_x, start_y, (255, 255, 255))
		start_y += self.linesize

	start_y += self.linesize * 3

	# Title
	title = "値を入力"
	title_x = center_x - self.font.size(title)[0] // 2
	self.draw_string(title, self.screen, title_x, start_y, (255, 255, 255))
	start_y += self.linesize * 2

	# Input box
	val = getattr(self, 'pending_value_buffer', "")
	input_text = f"> {val}_"
	text_w = self.font.size(input_text)[0]
	text_x = center_x - text_w // 2
	input_rect = RiftWizard.pygame.Rect(text_x, start_y, text_w, self.linesize)
	self.draw_string(input_text, self.screen, text_x, start_y, (255, 255, 255), mouse_content="input_box")
	self.ui_rects.append((input_rect, "input_box"))
	start_y += self.linesize * 2

	# Confirm button
	confirm = "確認"
	confirm_w = self.font.size(confirm)[0]
	confirm_x = center_x - confirm_w // 2
	confirm_rect = RiftWizard.pygame.Rect(confirm_x, start_y, confirm_w, self.linesize)
	self.draw_string(confirm, self.screen, confirm_x, start_y, (255, 255, 255), mouse_content="confirm")
	self.ui_rects.append((confirm_rect, "confirm"))

RiftWizard.PyGameView.draw_enter_mutator_value = draw_enter_mutator_value


def draw_options_menu(self):

	cur_x = self.screen.get_width() // 2 - self.font.size("アニメーション速度")[0]
	cur_y = self.screen.get_height() // 2 - self.linesize * RiftWizard.OPTION_MAX

	rect_w = self.font.size("アニメーション速度：超ターボ")[0]

	self.draw_string("プレイのしかた", self.screen, cur_x, cur_y, mouse_content=RiftWizard.OPTION_HELP, content_width=rect_w)
	cur_y += self.linesize

	self.draw_string("サウンド音量：　　　　%3d" % self.options["sound_volume"], self.screen, cur_x, cur_y, mouse_content=RiftWizard.OPTION_SOUND_VOLUME, content_width=rect_w)
	cur_y += self.linesize

	self.draw_string("ミュージック音量：　　%3d" % self.options["music_volume"], self.screen, cur_x, cur_y, mouse_content=RiftWizard.OPTION_MUSIC_VOLUME, content_width=rect_w)
	cur_y += self.linesize

	if self.options["spell_speed"] == 0:
		speed_fmt = "通常"
	elif self.options["spell_speed"] == 1:
		speed_fmt = "高速"
	if self.options["spell_speed"] == 2:
		speed_fmt = "ターボ"
	if self.options["spell_speed"] == 3:
		speed_fmt = "超ターボ"

	self.draw_string("アニメーション速度：%4s" % speed_fmt, self.screen, cur_x, cur_y, mouse_content=RiftWizard.OPTION_SPELL_SPEED, content_width=rect_w)
	cur_y += self.linesize

	self.draw_string("操作設定", self.screen, cur_x, cur_y, mouse_content=RiftWizard.OPTION_CONTROLS, content_width=rect_w)
	cur_y += self.linesize

	# self.draw_string("Smart Targeting: %5s" % str(self.options['smart_targeting']), self.screen, cur_x, cur_y, mouse_content=OPTION_SMART_TARGET, content_width=rect_w)
	# cur_y += self.linesize

	if self.game:
		self.draw_string("ゲームに戻る", self.screen, cur_x, cur_y, mouse_content=RiftWizard.OPTION_RETURN, content_width=rect_w)
		cur_y += self.linesize

		self.draw_string("セーブして終了", self.screen, cur_x, cur_y, mouse_content=RiftWizard.OPTION_EXIT, content_width=rect_w)
		cur_y += self.linesize

	else:
		self.draw_string("タイトルに戻る", self.screen, cur_x, cur_y, mouse_content=RiftWizard.OPTION_EXIT, content_width=rect_w)
		cur_y += self.linesize

RiftWizard.PyGameView.draw_options_menu = draw_options_menu


def draw_shop(self):

	# Spells: show spells show filters
	# Upgrades: show upgrades
	# Spell Upgrades: show upgrades for spell
	# Bestary: show all monsters (cannot purchase)

	self.shop_rects = []
	self.middle_menu_display.fill((0, 0, 0))
	self.draw_panel(self.middle_menu_display)

	# Draw Shrine Background
	if self.shop_type == RiftWizard.SHOP_TYPE_SHOP:
		cur_shop = self.game.cur_level.tiles[self.game.p1.x][self.game.p1.y].prop
		if cur_shop:
			image = RiftWizard.get_image(cur_shop.asset).subsurface((0, 0, RiftWizard.SPRITE_SIZE, RiftWizard.SPRITE_SIZE))
			big_shop = RiftWizard.pygame.transform.scale(image, (RiftWizard.SPRITE_SIZE * 32, RiftWizard.SPRITE_SIZE * 32))
			dx = (self.middle_menu_display.get_width() - big_shop.get_width()) // 2
			dy = (self.middle_menu_display.get_height() - big_shop.get_height()) // 2
			big_shop.fill((255, 255, 255, 90), special_flags=RiftWizard.pygame.BLEND_RGBA_MULT)
			self.middle_menu_display.blit(big_shop, (dx, dy))

	# Draw Spell Background
	if self.shop_type == RiftWizard.SHOP_TYPE_SPELL_UPGRADES:
		asset = RiftWizard.get_spell_asset(self.shop_upgrade_spell)
		image = RiftWizard.get_image(asset, alphafy=True)
		if image:
			image = image.subsurface((0, 0, RiftWizard.SPRITE_SIZE, RiftWizard.SPRITE_SIZE))
			big_shop = RiftWizard.pygame.transform.scale(image, (RiftWizard.SPRITE_SIZE * 32, RiftWizard.SPRITE_SIZE * 32))
			dx = (self.middle_menu_display.get_width() - big_shop.get_width()) // 2
			dy = (self.middle_menu_display.get_height() - big_shop.get_height()) // 2
			big_shop.fill((255, 255, 255, 90), special_flags=RiftWizard.pygame.BLEND_RGBA_MULT)
			self.middle_menu_display.blit(big_shop, (dx, dy))

	mx, my = self.get_mouse_pos()
	options = self.get_shop_options()

	spell_x_offset = self.border_margin + 18
	cur_x = spell_x_offset
	cur_y = self.linesize

	tag_offset = 16 * 32

	spell_column_width = 16 * 29
	level_x = cur_x + spell_column_width

	shoptions = self.get_shop_options()
	num_options = len(shoptions)

	if self.shop_type == RiftWizard.SHOP_TYPE_SPELLS:
		self.draw_string("呪文を習得する：", self.middle_menu_display, cur_x, cur_y)
		self.draw_string("SP", self.middle_menu_display, level_x - self.font.size("X")[0], cur_y, RiftWizard.COLOR_XP)
		self.draw_string("属性", self.middle_menu_display, cur_x + tag_offset, cur_y)
	if self.shop_type == RiftWizard.SHOP_TYPE_UPGRADES:
		self.draw_string("スキルを習得する：", self.middle_menu_display, cur_x, cur_y)
		self.draw_string("SP", self.middle_menu_display, level_x - self.font.size("X")[0], cur_y, RiftWizard.COLOR_XP)
		self.draw_string("属性", self.middle_menu_display, cur_x + tag_offset, cur_y)
	if self.shop_type == RiftWizard.SHOP_TYPE_SPELL_UPGRADES:
		self.draw_string("%sのアップグレード：" % translate(self.shop_upgrade_spell.name, "spell_name"), self.middle_menu_display, cur_x, cur_y)
	if self.shop_type == RiftWizard.SHOP_TYPE_SHOP:
		self.draw_string(translate(self.get_display_level().cur_shop.name, "shrine_name"), self.middle_menu_display, 0, cur_y, content_width=self.middle_menu_display.get_width(), center=True)
		cur_y += self.linesize
		self.draw_string(translate(self.get_display_level().cur_shop.description, "shrine_description"), self.middle_menu_display, 0, cur_y, content_width=self.middle_menu_display.get_width(), center=True)
	if self.shop_type == RiftWizard.SHOP_TYPE_BESTIARY:
		self.draw_string("ベスティアリ：%d種類のうち%d種類のモンスターを倒した" % (len(RiftWizard.all_monsters), RiftWizard.SteamAdapter.get_num_slain()), self.middle_menu_display, cur_x, cur_y)

	cur_y += self.linesize
	cur_y += self.linesize

	if not shoptions:
		if self.shop_type == RiftWizard.SHOP_TYPE_SHOP:
			self.draw_string("この祭壇で利用可能な呪文または装備品がありません", self.middle_menu_display, 0, cur_y, content_width=self.middle_menu_display.get_width(), center=True)
		elif self.shop_type in [RiftWizard.SHOP_TYPE_SPELLS]:
			self.draw_string("フィルターの条件を満たす呪文がありません", self.middle_menu_display, cur_x, cur_y, RiftWizard.HIGHLIGHT_COLOR)
		elif self.shop_type in [RiftWizard.SHOP_TYPE_UPGRADES]: # 本家側のバグ修正
			self.draw_string("フィルターの条件を満たすスキルがありません", self.middle_menu_display, cur_x, cur_y, RiftWizard.HIGHLIGHT_COLOR)

	start_index = self.shop_page * self.max_shop_objects
	end_index = start_index + self.max_shop_objects

	for opt in shoptions[start_index:end_index]:

		cur_x = spell_x_offset
		if self.shop_type in [RiftWizard.SHOP_TYPE_SPELLS, RiftWizard.SHOP_TYPE_UPGRADES]:
			self.draw_spell_icon(opt, self.middle_menu_display, cur_x, cur_y)
			cur_x += 20

		if isinstance(opt, RiftWizard.Equipment):
			icon = self.get_equipment_icon(opt)
			self.middle_menu_display.blit(icon, (cur_x, cur_y))
			cur_x += 20

		if self.shop_type == RiftWizard.SHOP_TYPE_SPELLS:
			fmt = translate(opt.name, "spell_name")
		elif self.shop_type == RiftWizard.SHOP_TYPE_UPGRADES:
			fmt = translate(opt.name, "skill_name")
		elif self.shop_type == RiftWizard.SHOP_TYPE_BESTIARY:
			fmt = translate(opt.name, "monster_name")
		else:
			if isinstance(opt, RiftWizard.Spell):
				fmt = translate(opt.name, "spell_name")
			elif isinstance(opt, RiftWizard.SpellUpgrade) or opt.prereq is not None:
				fmt = translate(opt.name, "upgrade_name")
			elif isinstance(opt, RiftWizard.Upgrade):
				fmt = translate(opt.name, "skill_name")
			elif isinstance(opt, RiftWizard.Equipment):
				fmt = translate(opt.name, "equipment_name")
			else:
				fmt = translate(opt.name, "item_name")
		cur_color = (255, 255, 255)

		if self.shop_type == RiftWizard.SHOP_TYPE_BESTIARY and not RiftWizard.SteamAdapter.has_slain(opt.name):
			fmt = "?????????????????????"
			cur_color = (100, 100, 100)

		if self.shop_type in [RiftWizard.SHOP_TYPE_SPELLS, RiftWizard.SHOP_TYPE_UPGRADES, RiftWizard.SHOP_TYPE_SPELL_UPGRADES]:
			cost = self.game.get_upgrade_cost(opt)
			if self.game.has_upgrade(opt):
				cur_color = (0, 255, 0)
			elif self.game.can_buy_upgrade(opt):
				cur_color = self.game.p1.discount_tag.color.to_tup() if self.game.p1.discount_tag in opt.tags else (255, 255, 255)
			else:
				cur_color = (100, 100, 100)

		if self.shop_type == RiftWizard.SHOP_TYPE_SHOP:
			width = self.middle_menu_display.get_width() - cur_x - self.border_margin
			self.draw_string(fmt, self.middle_menu_display, cur_x, cur_y, cur_color, mouse_content=opt, content_width=width)
		else:
			self.draw_string(fmt, self.middle_menu_display, cur_x, cur_y, cur_color, mouse_content=opt, content_width=spell_column_width)

			if hasattr(opt, "level") and isinstance(opt.level, int) and opt.level > 0:
				fmt = str(cost)
				if opt.name in self.game.p1.scroll_discounts:
					fmt += "*"
				self.draw_string(fmt, self.middle_menu_display, level_x, cur_y, cur_color)

		if self.shop_type in [RiftWizard.SHOP_TYPE_SPELLS, RiftWizard.SHOP_TYPE_UPGRADES]:
			tag_x = cur_x + tag_offset
			for tag in RiftWizard.Tags:
				if tag not in opt.tags:
					continue
				self.draw_string(self.reverse_tag_keys[tag], self.middle_menu_display, tag_x - 16, cur_y, tag.color.to_tup())
				tag_x += self.font.size(tag.name[0].translate(HAN2ZEN))[0]

		cur_y += self.linesize

	if self.shop_type in [RiftWizard.SHOP_TYPE_UPGRADES, RiftWizard.SHOP_TYPE_SPELLS]:
		# Draw filters
		cur_x = 16 * 40
		cur_y = self.linesize

		tag_width = self.middle_menu_display.get_width() - cur_x - self.border_margin

		cur_y += 2 * self.linesize
		self.draw_string("タグによるフィルター:", self.middle_menu_display, cur_x, cur_y)
		cur_y += self.linesize

		for tag in self.game.spell_tags:
			if tag == RiftWizard.Tags.Consumable:
				continue

			color = tag.color.to_tup() if tag in self.tag_filter else (150, 150, 150)
			self.draw_string(translate(tag.name, "tag_name"), self.middle_menu_display, cur_x + 24, cur_y, color, mouse_content=tag, content_width=tag_width)

			idx = 0

			for c in tag.name:
				if tag.name == "Chaos":
					self.draw_string("K", self.middle_menu_display, cur_x, cur_y, tag.color.to_tup())
					break
				if tag.name == "Slime":
					self.draw_string("Z", self.middle_menu_display, cur_x, cur_y, tag.color.to_tup())
					break
				if RiftWizard.tag_keys.get(c.lower(), None) == tag:
					self.draw_string(c.upper(), self.middle_menu_display, cur_x, cur_y, tag.color.to_tup())
					break
				idx += 1

			cur_y += self.linesize

		cur_y += self.linesize
		self.draw_string("効果によるフィルター：", self.middle_menu_display, cur_x, cur_y)
		cur_y += self.linesize

		for attr in RiftWizard.filter_attrs:
			attr_color = RiftWizard.attr_colors[attr].to_tup()
			color = attr_color if attr in self.attr_filter else (150, 150, 150)
			self.draw_string(translate(RiftWizard.format_attr(attr), "attr_name"), self.middle_menu_display, cur_x + 24, cur_y, color, mouse_content=attr, content_width=tag_width)

			idx = 0
			for c in attr:
				if RiftWizard.attr_keys.get(c.lower(), None) == attr:
					self.draw_string(c.lower(), self.middle_menu_display, cur_x, cur_y, attr_color)
					break
				idx += 1

			cur_y += self.linesize

		cur_y += self.linesize
		color = (255, 255, 255) if self.filter_unused else (150, 150, 150)
		self.draw_string("未習得", self.middle_menu_display, cur_x, cur_y, color, mouse_content=RiftWizard.UNPURCHASED_TARGET, content_width=tag_width)

		color = (255, 255, 255) if self.filter_unvictoried else (150, 150, 150)
		cur_y += self.linesize
		self.draw_string("未勝利", self.middle_menu_display, cur_x, cur_y, color, mouse_content=RiftWizard.UNVICTORIED_TARGET, content_width=tag_width)

	cur_x = spell_x_offset
	cur_y = self.linesize * (self.max_shop_objects + 4)
	max_shop_pages = self.get_max_shop_pages()

	if max_shop_pages > 1:

		can_prev = self.shop_page > 0
		prev_fmt = "<<<<"
		cur_color = (255, 255, 255) if can_prev else RiftWizard.HIGHLIGHT_COLOR
		self.draw_string(prev_fmt, self.middle_menu_display, cur_x, cur_y, cur_color, mouse_content=RiftWizard.TOOLTIP_PREV if can_prev else None)

		cur_x += self.font.size(prev_fmt + "    ")[0]
		fmt = "ページ %d/%d" % (self.shop_page + 1, self.get_max_shop_pages())
		self.draw_string(fmt, self.middle_menu_display, cur_x, cur_y)

		cur_x += self.font.size(fmt + "    ")[0]
		# cur_x = spell_x_offset + spell_column_width - self.font.size(prev_fmt)[0]

		can_next = self.shop_page < max_shop_pages - 1
		next_fmt = ">>>>"
		cur_color = (255, 255, 255) if can_next else RiftWizard.HIGHLIGHT_COLOR
		self.draw_string(next_fmt, self.middle_menu_display, cur_x, cur_y, cur_color, mouse_content=RiftWizard.TOOLTIP_NEXT if can_next else None)

	self.screen.blit(self.middle_menu_display, (self.h_margin, 0))


RiftWizard.PyGameView.draw_shop = draw_shop

ZEN = "　".join(chr(0xFF01 + i) for i in range(94))
HAN = " ".join(chr(0x21 + i) for i in range(94))
ZEN2HAN = str.maketrans(ZEN, HAN)
HAN2ZEN = str.maketrans(HAN, ZEN)


def draw_string(self, string, surface, x, y, color=(255, 255, 255), mouse_content=None, content_width=None, center=False, char_panel=False, font=None):
	string = string.translate(HAN2ZEN)
	if not font:
		font = self.font

	width = content_width if content_width else font.size(string)[0]
	if center:
		line_size = self.font.size(string)[0]
		x = x + (width - line_size) // 2
		width = line_size

	if mouse_content is not None:
		rel_rect = RiftWizard.pygame.Rect(x, y - 2, width, self.linesize)
		self.make_content_rect(surface, rel_rect, mouse_content, enable_highlight=(not char_panel))

	string_surface = font.render(string, True, color)
	surface.blit(string_surface, (x, y))

RiftWizard.PyGameView.draw_string = draw_string


def draw_title(self):

	m_loc = self.get_mouse_pos()

	if RiftWizard.SIZE == RiftWizard.SIZE_LARGE:
		cur_x = 25 * RiftWizard.SPRITE_SIZE * 2 - 12
		cur_y = 23 * RiftWizard.SPRITE_SIZE * 2 + 5
		title_x = self.screen.get_width() // 2 - self.title_image.get_width() // 2
		title_y = 40

	if RiftWizard.SIZE == RiftWizard.SIZE_MED:
		cur_x = 20 * RiftWizard.SPRITE_SIZE * 2 - 12
		cur_y = 23 * RiftWizard.SPRITE_SIZE * 2 - 10
		title_x = self.screen.get_width() // 2 - self.title_image.get_width() // 2
		title_y = 20

	if RiftWizard.SIZE == RiftWizard.SIZE_SMALL:
		cur_x = 16 * RiftWizard.SPRITE_SIZE * 2 - 1
		cur_y = 18 * RiftWizard.SPRITE_SIZE * 2 + 5
		title_y = -120
		title_x = self.screen.get_width() // 2 - self.title_image.get_width() // 2

	title_origin = (title_x, title_y)

	self.screen.blit(self.title_image, title_origin)

	rect_w = self.font.size("新しい冒険を始める")[0]

	opts = []
	if RiftWizard.can_continue_game():
		opts.append((RiftWizard.TITLE_SELECTION_LOAD, "冒険の続きから"))
		opts.append((RiftWizard.TITLE_SELECTION_ABANDON, "冒険をあきらめる"))
	else:
		opts.append((RiftWizard.TITLE_SELECTION_NEW, "新しい冒険を始める"))

	opts.extend([(RiftWizard.TITLE_SELECTION_OPTIONS, "オプション"), (RiftWizard.TITLE_SELECTION_BESTIARY, "ベスティアリ"), (RiftWizard.TITLE_SELECTION_DISCORD, "Discord"), (RiftWizard.TITLE_SELECTION_EXIT, "終了")])

	for o, w in opts:
		cur_color = (255, 255, 255)
		self.draw_string(w, self.screen, cur_x, cur_y, cur_color, mouse_content=o, content_width=rect_w)
		cur_y += self.linesize + 2

	cur_y += 3 * self.linesize

	# self.draw_string("Wins:   %d" % SteamAdapter.get_stat('w'), self.screen, cur_x, cur_y)
	cur_y += self.linesize
	# self.draw_string("Loses:  %d" % SteamAdapter.get_stat('l'), self.screen, cur_x, cur_y)
	cur_y += self.linesize
	# self.draw_string("Streak: %d" % SteamAdapter.get_stat('s'), self.screen, cur_x, cur_y)

	# Draw border of tiles
	tileset = "stone"
	big_tiles = [RiftWizard.pygame.transform.scale(tile, (32, 32)) for tile in self.wall_tiles[tileset]]

	screen_tile_height = self.screen.get_height() // (RiftWizard.SPRITE_SIZE * 2)
	screen_tile_width = self.screen.get_width() // (RiftWizard.SPRITE_SIZE * 2)


RiftWizard.PyGameView.draw_title = draw_title


def draw_turn_stats(self):
	cur_x = self.border_margin
	cur_y = self.border_margin
	linesize = self.linesize
	turn_summary = self.game.cur_level.turn_summary

	char_limit = 14  # Todo- make this different at lower resolutions?
	stat_fmt = " %-14s%5d"

	if RiftWizard.SIZE == RiftWizard.SIZE_MED:
		char_limit = 14
		stat_fmt = " %-14s%5d"
	if RiftWizard.SIZE == RiftWizard.SIZE_SMALL:
		char_limit = 11
		stat_fmt = " %-11s%5d"

	last_action = self.game.p1.last_action
	if last_action is not None:
		action_type = type(last_action)
		if action_type == RiftWizard.MoveAction:
			action_str = "あなたは移動した"
		elif action_type == RiftWizard.CastAction:
			action_str = "あなたは%sを唱えた" % translate(last_action.spell.name, "spell_name")
		elif action_type == RiftWizard.PassAction:
			action_str = "あなたは待機した"
		elif action_type == RiftWizard.StunnedAction:
			action_str = "あなたは%dターンの間%s状態だった" % (last_action.duration, translate(last_action.buff.name, "buff_name"))

		self.draw_string(action_str, self.examine_display, cur_x, cur_y)
		cur_y += 2 * linesize

	if turn_summary.damage_dealt:
		total_dmg = sum(turn_summary.damage_dealt.values())
		self.draw_string("与えたダメージ：%12d" % total_dmg, self.examine_display, cur_x, cur_y)
		cur_y += linesize

		sorted_items = sorted(turn_summary.damage_dealt.items(), key=lambda t: -t[1])

		for src, dmg in sorted_items:
			src = translate(src, "log_name")
			self.draw_string(stat_fmt % (src[:char_limit], dmg), self.examine_display, cur_x, cur_y)
			cur_y += linesize

		cur_y += linesize

		RiftWizard.SteamAdapter.record_damage_dealt(total_dmg)

	if turn_summary.self_damage_taken:
		total_dmg = sum(turn_summary.self_damage_taken.values())
		self.draw_string("受けたダメージ：%12d" % total_dmg, self.examine_display, cur_x, cur_y)
		cur_y += linesize
		for src, dmg in turn_summary.self_damage_taken.items():
			src = translate(src, "log_name")
			self.draw_string(stat_fmt % (src[:char_limit], dmg), self.examine_display, cur_x, cur_y)
			cur_y += linesize

		cur_y += linesize

	if turn_summary.ally_damage_taken:
		total_dmg = sum(turn_summary.ally_damage_taken.values())
		self.draw_string("味方が受けたダメージ：%9d" % total_dmg, self.examine_display, cur_x, cur_y)
		cur_y += linesize
		for src, dmg in turn_summary.ally_damage_taken.items():
			src = translate(src, "log_name")
			self.draw_string(stat_fmt % (src[:char_limit], dmg), self.examine_display, cur_x, cur_y)
			cur_y += linesize

		cur_y += linesize

	if turn_summary.enemy_kill_counts:
		total_kills = sum(turn_summary.enemy_kill_counts.values())
		self.draw_string("倒した敵：%15d" % total_kills, self.examine_display, cur_x, cur_y)
		cur_y += linesize
		for name, kills in turn_summary.enemy_kill_counts.items():
			name = translate(name, "log_name")
			self.draw_string(stat_fmt % (name[:char_limit], kills), self.examine_display, cur_x, cur_y)
			cur_y += linesize
		cur_y += linesize

	if turn_summary.ally_kill_counts:
		total_kills = sum(turn_summary.ally_kill_counts.values())
		self.draw_string("倒された味方：%13d" % total_kills, self.examine_display, cur_x, cur_y)
		cur_y += linesize
		for name, kills in turn_summary.ally_kill_counts.items():
			name = translate(name, "log_name")
			self.draw_string(stat_fmt % (name[:char_limit], kills), self.examine_display, cur_x, cur_y)
			cur_y += linesize
		cur_y += linesize


RiftWizard.PyGameView.draw_turn_stats = draw_turn_stats


def draw_wrapped_string(self, string, surface, x, y, width, color=(255, 255, 255), center=False, indent=False, extra_space=False):
	lines = [l for l in string.split("\n") if l]

	cur_x = x
	cur_y = y
	linesize = self.linesize
	num_lines = 0

	char_width = 16
	chars_per_line = width // char_width
	for line in lines:
		# words = line.split(' ')
		# This regex separates periods, spaces, com`, and tokens
		exp = r"\[.*?\]|-\d+%?|\d+%?|."
		words = re.findall(exp, line)
		words.reverse()
		cur_line = ""
		chars_left = chars_per_line

		# Start each line all the way to the left
		cur_x = x
		assert (all(len(word) < chars_per_line) for word in words)

		while words:
			cur_color = color

			word = words.pop()
			if word != " ":

				# Process complex tooltips- strip off the []s and look up the color
				if word and word[0] == '[' and word[-1] == ']':
					tokens = word[1:-1].split(':')
					if len(tokens) == 1:
						word = tokens[0] # todo- fmt attribute?
						cur_color = RiftWizard.tooltip_colors[word.lower()].to_tup()
					elif len(tokens) == 2:
						word = tokens[0].replace('_', ' ')
						cur_color = RiftWizard.tooltip_colors[tokens[1].lower()].to_tup()

				max_size = chars_left if word in ["　", "。", "、", "・", "％"] else chars_left - 1
				if len(word) > max_size:
					cur_y += linesize
					num_lines += 1
					# Indent by one for next line
					cur_x = x
					chars_left = chars_per_line

				self.draw_string(word, surface, cur_x, cur_y, cur_color, content_width=width)

			cur_x += (len(word)) * char_width
			chars_left -= len(word)

		cur_y += linesize
		num_lines += 1
		if extra_space:
			cur_y += linesize
			num_lines += 1

	return num_lines


RiftWizard.PyGameView.draw_wrapped_string = draw_wrapped_string


def new_game(self, mutators=None, trial_name=None, seed=None):

	# If you are overwriting an old game, break streak
	if RiftWizard.can_continue_game():
		RiftWizard.SteamAdapter.set_stat("s", 0)
		RiftWizard.SteamAdapter.set_stat("l", RiftWizard.SteamAdapter.get_stat("l") + 1)

	self.game = RiftWizard.Game(save_enabled=True, mutators=mutators, trial_name=trial_name, seed=seed)
	self.message = text.intro_text

	if mutators:
		self.message += "\n\n\n\n変更点："
		for mutator in mutators:
			self.message += "\n" + translate_lines(mutator.description, "trial_description")

	self.center_message = True
	self.state = RiftWizard.STATE_MESSAGE

	self.play_battle_music()

	self.make_level_screenshot()
	RiftWizard.SteamAdapter.set_presence_level(1)

RiftWizard.PyGameView.new_game = new_game


def open_abandon_prompt(self):
	self.state = RiftWizard.STATE_CONFIRM
	self.confirm_text = "本当に現在の冒険をあきらめますか？"
	self.confirm_yes = self.confirm_abandon
	self.confirm_no = self.abort_abandon
	self.examine_target = False

RiftWizard.PyGameView.open_abandon_prompt = open_abandon_prompt


def open_buy_prompt(self, item):
	self.play_sound("menu_confirm")
	self.state = RiftWizard.STATE_CONFIRM
	self.confirm_yes = self.confirm_buy
	self.confirm_no = self.abort_buy

	self.chosen_purchase = item

	if isinstance(item, RiftWizard.Equipment):
		self.confirm_text = "%sを獲得しますか？" % translate(item.name, "equipment_name")
	elif isinstance(item, RiftWizard.ShrineBuff):
		RiftWizard.attr = self.chosen_purchase.name.replace(self.chosen_purchase.shrine_name + " ", "").lower()
		self.confirm_text = "%sを%sに使いますか？" % (self.game.cur_level.cur_shop.name, self.chosen_purchase.prereq.name)
	else:
		if isinstance(self.chosen_purchase, RiftWizard.Spell):
			japanese_name = translate(self.chosen_purchase.name, "spell_name")
		elif isinstance(self.chosen_purchase, RiftWizard.SpellUpgrade) or self.chosen_purchase.prereq is not None:
			japanese_name = translate(self.chosen_purchase.name, "upgrade_name")
		elif isinstance(self.chosen_purchase, RiftWizard.Upgrade):
			japanese_name = translate(self.chosen_purchase.name, "skill_name")
		if isinstance(self.game.cur_level.cur_shop, RiftWizard.AmnesiaShop) and isinstance(item, RiftWizard.Spell):
			self.confirm_text = "%sを忘れますか？" % (japanese_name)
		elif self.shop_type == RiftWizard.SHOP_TYPE_SHOP:
			self.confirm_text = "%sを習得しますか？" % (japanese_name)
		else:
			cost = self.game.get_upgrade_cost(self.chosen_purchase)
			self.confirm_text = "%sSPで%sを習得しますか？" % (cost, japanese_name)

	# Default to no (?)
	self.examine_target = False

RiftWizard.PyGameView.open_buy_prompt = open_buy_prompt


def draw_confirm(self):
	self.middle_menu_display.fill((0, 0, 0))

	cur_y = self.middle_menu_display.get_height() // 2 - 3 * self.linesize
	cur_x = (self.middle_menu_display.get_width() - self.font.size(self.confirm_text)[0]) // 2
	self.draw_string(self.confirm_text, self.middle_menu_display, cur_x, cur_y)

	cur_y += 2 * self.linesize
	cur_x = (self.middle_menu_display.get_width()) // 4
	self.draw_string("はい", self.middle_menu_display, cur_x, cur_y, mouse_content=True)

	cur_x = (self.middle_menu_display.get_width()) * 3 // 4 - self.font.size("いいえ")[0]
	self.draw_string("いいえ", self.middle_menu_display, cur_x, cur_y, mouse_content=False)

	self.screen.blit(self.middle_menu_display, (self.h_margin, 0))

RiftWizard.PyGameView.draw_confirm = draw_confirm


# scratch.py
# Shrines.py
# Patch 2時点ではほとんどのShrineクラスが利用されていない様子
def shrines_sorcery_shield_stack_on_init(self):
	self.name = "%s・プロテクション" % translate(self.tag.name, "tag_name")
	self.stack_type = RiftWizard.STACK_NONE
	self.resists[self.tag] = 100
	self.color = self.tag.color


Shrines.SorceryShieldStack.on_init = shrines_sorcery_shield_stack_on_init


# SpecialLevels.py
# Spells.py

original_init = Spells.RepeaterCast.__init__
def spells_repeater_cast_init(self, *args, **kwargs):
	original_init(self, *args, **kwargs)
	self.name = translate(self.spell.name, "spell_name") +"・リピーター"
	self.description = "あなたのターンの終了時に%sをもう一度唱える。" % (translate(self.spell.name, "spell_name"))
	
Spells.RepeaterCast.__init__ = spells_repeater_cast_init

def spells_elemental_eye_buff_init(self, element, damage, freq, spell):
	RiftWizard.Buff.__init__(self)
	self.element = element
	self.damage = damage
	self.freq = max(1, freq)
	self.cooldown = freq
	self.color = element.color
	self.buff_type = RiftWizard.BUFF_TYPE_BLESS
	self.stack_type = RiftWizard.STACK_REPLACE

	freq_str = "毎ターン" if self.freq == 1 else ("%dターンごとに" % self.freq)
	self.description = "%s視界内のランダムな敵1体に%d%sダメージを与える。" % (freq_str, self.damage, translate(self.element.name, "tag_name"))
	self.spell = spell


Spells.ElementalEyeBuff.__init__ = spells_elemental_eye_buff_init


def spells_echo_cast_init(self, spell):
	RiftWizard.Buff.__init__(self)
	self.spell = spell
	self.name = "エコー・キャスト（" + translate(spell.name, "spell_name") + "）"
	self.description = ("%dターン後に" % self.turns_left) + translate(spell.name, "spell_name") + "を再詠唱する。"
	self.color = spell.tags[0].color
	self.stack_type = RiftWizard.STACK_INTENSITY


Spells.EchoCast.__init__ = spells_echo_cast_init


def spells_echo_on_advance(self):
	self.description = ("%dターン後に" % self.turns_left) + translate(self.spell.name, "spell_name") + "を再詠唱する。"


Spells.EchoCast.on_advance = spells_echo_on_advance

# SteamAdapter.py
# text.py
RiftWizard.LEARN_SPELL_TARGET = RiftWizard.TooltipExamineTarget("新しい呪文を習得する")
RiftWizard.LEARN_SKILL_TARGET = RiftWizard.TooltipExamineTarget("新しいスキルを習得する")
RiftWizard.CHAR_SHEET_TARGET = RiftWizard.TooltipExamineTarget("新しい呪文とスキルを習得する")
RiftWizard.INSTRUCTIONS_TARGET = RiftWizard.TooltipExamineTarget("プレイのしかたを学ぶ")
RiftWizard.OPTIONS_TARGET = RiftWizard.TooltipExamineTarget("オプションを設定する")
RiftWizard.STUNNED_TARGET = RiftWizard.TooltipExamineTarget("このターンは移動も詠唱もできない。\nターンをパスしなければならない。\n（自分自身をクリックするか、テンキーの５を押せ）")
RiftWizard.REROLL_PORTALS_TARGET = RiftWizard.TooltipExamineTarget("すべてのリフトの行き先をリロールする。各レルムで１回しかできない。")

text.intro_text = """
魔法使いよ、世界の廃墟によくぞ戻った。

汝がまどろむ間に永劫が過ぎ去った。
汝は眠りの中で数多の世界を巡ってきた。

孤独な老いた魔法使いよ、アヴァロンのために嘆くがいい！
かつての愛と美は、混沌と破滅へと変貌した。

汝の愛したアヴァロンも、そしてその忠実な下僕たる汝も。

かつては偉大な魔法使いであった汝も、
その記憶と魔法は薄れ去った。

今、復讐への渇望が汝を目覚めさせる。
暗黒の魔法使い、モードレッドの存在は近い。

汝の力を取り戻せ。
モードレッドを討て。
アヴァロンの復讐を。
"""

text.victory_text = """暗黒の魔法使いは討たれた。

彼の獣たちは破れ、鎮められた。

アヴァロンの美は再び築かれるだろう。

汝の魂は、再び眠りにつき夢見ることを許された。
"""

text.welcome_text = """WELCOME
リフト・ウィザードへようこそ。
Ｈを押すとゲームのすべての操作と詳細が表示される。
調べたいものにマウスカーソルを重ねると詳細が表示される。
Ｓを押すと魔法を習得できる。"""

text.deploy_text = """
あなたはリフトの半ばに足を踏み入れた。
次の世界で現れる地点を選ぶことができる（Enterか左クリック）。
あるいは、このリフトから抜け出して前の世界に戻ることもできる（Escか右クリック）。
注意せよ。一度入れば戻る方法はない。"""

text.how_to_play = """プレイのしかた

20階層を踏破し、宿敵を倒すことでゲームに勝利できる。
次の階層に進むには、今いる階層のすべての敵を倒さなければならない。

階層を完了したら、リフトに入って内側を覗き込める。
空きタイルをクリックすればそこに瞬間移動する。Escを押せば中止する。
新たな階層に入ったら、その階層を完了するまで出ることはできない。注意せよ。

すべての呪文とスキルは、キャラクターシートでスキルポイント（SP)を使って購入できる。
各呪文はキャラクターシートでSPを使って個別にアップグレードできる。

呪文を唱えるにはチャージを消費する。唱えるたびにその呪文のチャージが1減る。
マナ・ポーションを飲むか、階層を完了することでチャージがすべて回復する。

操作方法：

H：ヘルプ（この画面）　　C:キャラクターシート　　S:呪文を習得する　　K:スキルを習得する

左クリック：カーソルの地点に移動、または、選択中の呪文を唱える
右クリック：現在の呪文をキャンセルする、または、現在のメニューを閉じる

テンキー：
7 8 9
4   6　→　対応する方向に1歩移動する
1 2 3

テンキーの5：1ターン待機する（または、連続詠唱中の場合は連続詠唱を続ける）

		1 2 3 4 5 6 7 8 9 0: 呪文1-10を唱える／選択する
Shift + 1 2 3 4 5 6 7 8 9 0: 呪文11-20を唱える／選択する
Alt   + 1 2 3 4 5 6 7 8 9 0: アイテム1-10を使う／選択する

テンキー／マウス：対象選択のカーソルを動かす
Esc：呪文の対象選択をキャンセルする
Enter：現在の呪文を唱える、または、現在地のポータルに入る

高度な操作：

ｌ：視線を表示する　　　　　　　　ｔ：脅威のあるタイルを表示する
Ｔａｂ：次の対象を選択する　　　　ｍ：メッセージログを表示する

v:見る（見たいタイルを選択する。Tabでタイルを自動選択する）
w:歩く（移動先のタイルを選択する。Tabでタイルを自動選択する）
a:すべてのアイテムを自動で回収する（階層完了後のみ）
Shift＋↑／↓:選択中の呪文のホットキーを変更（キャラクターシートでのみ）
i:現在地のタイルに対してアクションする（ポータルに入る、宝箱を開く）
pgup/pgdown:呪文のアップグレードの説明を表示する（呪文の説明を表示しているときのみ）
"""

text.advanced_tips = """状態

スタン：行動できない。
毒：1毒ダメージを毎ターン受ける。HPを回復できない。
恐怖：自分の意思で行動できない。効果中の各ターン、自動的に敵から遠ざかるように移動を試みる。
石化：行動できない。アイス耐性とライトニング耐性を100得る。物理耐性とファイア耐性を75得る。
ガラス化：行動できない。アイス耐性とライトニング耐性を100得る。ファイア耐性を75得る。物理耐性を100失う。
凍結：行動できない。ファイアダメージか物理ダメージを受けると終了する。アイス耐性が100のユニットには効果がない。
浸水：ファイア耐性を50得る。アイス耐性とライトニング耐性を50失う。
狂乱：他のすべてのユニットに対して敵対する。味方にも攻撃し、味方からも攻撃される。
盲目：すべての呪文の射程が1に減少する。
沈黙：呪文を唱えられない。
連続詠唱：他のアクションをしない限り、唱えた呪文を同じ対象に唱え続ける。
シールド（SH)：SHを持つユニットがダメージを受けるとき、HPを失わずに1SHを失う。
スタン耐性：スタン・恐怖・石化・ガラス化・凍結・沈黙を取り除き、耐性を得る。
"""

RiftWizard.WELCOME_TARGET = RiftWizard.TooltipExamineTarget(text.welcome_text)
RiftWizard.DEPLOY_TARGET = RiftWizard.TooltipExamineTarget(text.deploy_text)

RiftWizard.UNPURCHASED_TARGET = RiftWizard.TooltipExamineTarget("習得したことがない項目のみを表示する。")
RiftWizard.UNVICTORIED_TARGET = RiftWizard.TooltipExamineTarget("習得してゲームに勝利したことがない項目のみを表示する。")


# Upgrades.py
def upgrades_dragon_scales_buff_init(self, damage_type):
	RiftWizard.Buff.__init__(self)
	self.resists[damage_type] = 100
	self.name = "%sスケイルズ" % translate(damage_type.name, "tag_name")
	self.color = damage_type.color


RiftWizard.DragonScalesBuff.__init__ = upgrades_dragon_scales_buff_init


def upgrades_echomancy_on_init(self):
	self.name = "エコーマンシー：%s" % translate(self.spell.name, "spell_name")
	self.description = "次に%sを唱えるために使われるチャージを変換する。" % translate(self.spell.name, "spell_name")
	self.color = RiftWizard.Tags.Arcane.color
	# Do nothing in this buff, just let the upgrade do stuff by checking for this buff


RiftWizard.Echomancy.on_init = upgrades_echomancy_on_init


def upgrades_hypocrisy_stack_on_init(self):
	self.name = "%s・ヒポクラシー（%d）" % (translate(self.tag.name, "tag_name"), self.level)
	self.description = "次に唱える呪文がレベル%d以下の%s呪文なら、そのコストは支払わない。" % (self.level, translate(self.tag.name, "tag_name"))
	self.color = self.tag.color
	self.owner_triggers[RiftWizard.EventOnSpellCast] = self.on_spell_cast
	self.stack_type = RiftWizard.STACK_INTENSITY


RiftWizard.HypocrisyStack.on_init = upgrades_hypocrisy_stack_on_init

# TODO Mで出るメッセージ履歴


### 調査

import itertools

def create_instance(cls):
    sig = inspect.signature(cls.__init__)
    params = sig.parameters

    # self を除いた引数に対して、デフォルト値 or None を設定
    args = {
        name: (param.default if param.default is not inspect.Parameter.empty else None)
        for name, param in params.items()
        if name != "self"
    }

    return cls(**args)

def get_all_subclasses(cls, exclude=None):
	if exclude is None:
		exclude = []
	subclasses = set(cls.__subclasses__())
	for subclass in cls.__subclasses__():
		if any(issubclass(subclass, ex) for ex in exclude):
			continue
		subclasses.update(get_all_subclasses(subclass, exclude))
	return subclasses


# subclass_names = [subclass.__name__ for subclass in subclasses]
failed_classes = []

def check_all_subclasses(dic_suffix, subclasses):
	dic_name = dic_suffix + "_name"
	dic_desc = dic_suffix + "_description"
	for c in subclasses:
		instance = None
		try:
			instance = create_instance(c)
			# print(f"{dic_name}|{c.__name__}|{instance.name}|{translate(instance.name,dic_name)}")
		except Exception as e:
			failed_classes.append(c.__name__)
			continue

		for attr in ['description', 'get_description', 'tooltip', 'get_tooltip']:
			try:
				if hasattr(instance, attr):
					value = getattr(instance, attr)
				if callable(value):
					value = value()
				if isinstance(value, str):
					for line in value.split('\n'):
						# print(f"{dic_desc}|{c.__name__}|{line}|{translate(line,dic_desc)}")
						continue
			except Exception as e:
				# print(f"{dic_desc}|{c.__name__}|ERROR")
				continue
			

def check_all_consumable():
	for consumable_def in [item[0] for item in RiftWizard.all_consumables ]:
		consumable = consumable_def()
		name = consumable.name
		translate_name = translate(name,"item_name")
		# print(f"item_name|item|{name}|{translate_name}")
		desc = consumable.description
		translate_desc = translate_lines(desc,"item_description")
		# print(f"item_description|item|{desc}|{translate_desc}")


def check_all_upgrade():
	for c in RiftWizard.all_player_spell_constructors:
		instance = create_instance(c)
		for upgrade in instance.upgrades.values():
			name = upgrade[2] if len(upgrade) > 2 else ""
			translate_name = translate(name,"upgrade_name")
			# print(f"upgrade_name|{c.__name__}|{name}|{translate_name}")
			desc = upgrade[3] if len(upgrade) > 3 else ""
			p = re.compile('\{[^\}]*\}') # {...} を * に置換
			desc = p.sub('*', desc)
			translate_desc = translate_lines(desc,"upgrade_description")
			# print(f"upgrade_description|{c.__name__}|{desc}|{translate_desc}")

def check_all_weekly_mods():
	trial_mutators = [trial.mutators for trial in RiftWizard.all_trials]
	trial_mutators = list(itertools.chain.from_iterable(trial_mutators))
	for mod in RiftWizard.weekly_mods + RiftWizard.weekly_boons + trial_mutators:
		desc = mod.description
		mod_desc = translate_lines(desc,"trial_description")
		# print(f"trial_description|{type(mod).__name__}|{desc}|{mod_desc}")


try:
	check_all_subclasses("buff", get_all_subclasses(RiftWizard.Buff, exclude=[RiftWizard.Equipment, RiftWizard.Upgrade]))
	check_all_subclasses("cloud", get_all_subclasses(RiftWizard.Cloud, exclude=[]))
	check_all_subclasses("item", get_all_subclasses(RiftWizard.Item, exclude=[]))
	check_all_subclasses("equipment", get_all_subclasses(RiftWizard.Equipment, exclude=[]))
	check_all_subclasses("skill", RiftWizard.skill_constructors)
	check_all_subclasses("spell", RiftWizard.all_player_spell_constructors)
	check_all_subclasses("monster_spell", get_all_subclasses(RiftWizard.Spell, exclude=[]))
	check_all_consumable()
	check_all_upgrade()
	check_all_weekly_mods()

except Exception as e:
	error_class = type(e)
	error_description = str(e)
	err_msg = '%s: %s' % (error_class, error_description)
	print(err_msg)
	tb = traceback.extract_tb(sys.exc_info()[2])
	trace = traceback.format_list(tb)
	print('---- traceback ----')
	for line in trace:
		if '~^~' in line:
			print(line.rstrip())
		else:
			text = re.sub(r'\n\s*', ' ', line.rstrip())
			print(text)
	print('------------------')


# if failed_classes:
# 	print("Failed to instantiate the following classes:")
# 	for class_name in failed_classes:
# 		print(class_name)



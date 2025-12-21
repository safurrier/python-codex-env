import { ItemType, AnimationState } from './items';

export interface Interaction {
  id: string;
  participants: string[]; // IDs of items involved
  type: InteractionType;
  energyValue: number; // How much this interaction contributes to connection energy
  isActive: boolean;
}

export enum InteractionType {
  // Person to Person
  PARENT_CHILD = 'parent_child',
  GRANDPARENT_CHILD = 'grandparent_child',
  PARTNERS = 'partners',
  FAMILY_GATHERING = 'family_gathering',
  PET_PERSON = 'pet_person',

  // Person to Gift
  CHILD_GIFT = 'child_gift',
  ADULT_GIFT = 'adult_gift',
  GIFT_OPENING = 'gift_opening',
  GIFT_GIVING = 'gift_giving',
  WATCHING_OPENING = 'watching_opening',

  // Person to Decoration
  CHILD_TREE = 'child_tree',
  FAMILY_TREE = 'family_tree',
  HEIRLOOM_ORNAMENT = 'heirloom_ornament',

  // Person to Comfort
  FIREPLACE_GATHERING = 'fireplace_gathering',
  COCOA_MOMENT = 'cocoa_moment',
  BLANKET_SHARE = 'blanket_share',
  FAMILY_MEAL = 'family_meal',
  MUSIC_ENJOYMENT = 'music_enjoyment',

  // Person to Tradition
  STORYTELLING = 'storytelling',
  PHOTO_SHARING = 'photo_sharing',
  MOVIE_WATCHING = 'movie_watching',
  SPIRITUAL_MOMENT = 'spiritual_moment',

  // Special Easter Eggs
  FOUR_GENERATIONS = 'four_generations',
  PET_GIFT = 'pet_gift',
  QUIET_MOMENT = 'quiet_moment',
  HANDMADE_TREASURE = 'handmade_treasure',
  CHRISTMAS_CHAOS = 'christmas_chaos',
  EMPTY_CHAIR = 'empty_chair',
  NEW_TRADITION = 'new_tradition',
}

export interface InteractionRule {
  type: InteractionType;
  requiredItems: Array<{
    category?: string;
    type?: ItemType;
    minCount?: number;
    maxDistance?: number; // pixels
  }>;
  energyValue: number;
  animations?: Map<string, AnimationState>; // item ID -> animation state
  effects?: InteractionEffect[];
}

export interface InteractionEffect {
  type: EffectType;
  target?: string; // item ID, or 'all' for room-wide
  duration?: number; // ms, undefined for permanent
  intensity?: number; // 0-1
}

export enum EffectType {
  GLOW = 'glow',
  SPARKLE = 'sparkle',
  WARMTH = 'warmth',
  LIGHT_RAY = 'light_ray',
  SNOW_INSIDE = 'snow_inside',
  FADE_OTHERS = 'fade_others',
  FLASHBACK = 'flashback',
  SACRED_FEELING = 'sacred_feeling',
}

export interface ProximityCheck {
  item1: string;
  item2: string;
  distance: number;
}

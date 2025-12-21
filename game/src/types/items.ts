export enum ItemCategory {
  PEOPLE = 'people',
  GIFTS = 'gifts',
  DECORATIONS = 'decorations',
  COMFORT = 'comfort',
  TRADITIONS = 'traditions',
}

export enum PersonType {
  CHILD = 'child',
  PARENT = 'parent',
  GRANDPARENT = 'grandparent',
  TEEN = 'teen',
  PET = 'pet',
  PARTNER = 'partner',
}

export enum GiftType {
  SMALL_BOX = 'small_box',
  MEDIUM_BOX = 'medium_box',
  LARGE_BOX = 'large_box',
  GIFT_BAG = 'gift_bag',
  STOCKING = 'stocking',
  HANDMADE = 'handmade',
  PRACTICAL = 'practical',
  EXPERIENCE = 'experience',
}

export enum DecorationType {
  TREE = 'tree',
  ORNAMENT = 'ornament',
  HEIRLOOM_ORNAMENT = 'heirloom_ornament',
  HANDMADE_ORNAMENT = 'handmade_ornament',
  STRING_LIGHTS = 'string_lights',
  WALL_STOCKING = 'wall_stocking',
  WREATH = 'wreath',
  GARLAND = 'garland',
  CANDLE = 'candle',
  TREE_TOPPER = 'tree_topper',
}

export enum ComfortType {
  FIREPLACE = 'fireplace',
  HOT_COCOA = 'hot_cocoa',
  COFFEE = 'coffee',
  BLANKET = 'blanket',
  BREAKFAST = 'breakfast',
  MUSIC_PLAYER = 'music_player',
  COOKIES = 'cookies',
}

export enum TraditionType {
  PHOTO_ALBUM = 'photo_album',
  STORY_BOOK = 'story_book',
  HOLIDAY_MOVIE = 'holiday_movie',
  ADVENT_CALENDAR = 'advent_calendar',
  NATIVITY_SCENE = 'nativity_scene',
  RECIPE_BOOK = 'recipe_book',
  SANTA_LETTER = 'santa_letter',
  CHRISTMAS_CARDS = 'christmas_cards',
}

export type ItemType = PersonType | GiftType | DecorationType | ComfortType | TraditionType;

export interface Position {
  x: number;
  y: number;
}

export interface BaseItem {
  id: string;
  category: ItemCategory;
  type: ItemType;
  position: Position;
  zIndex: number;
}

export interface PersonItem extends BaseItem {
  category: ItemCategory.PEOPLE;
  type: PersonType;
  animationState: AnimationState;
  interactionTarget?: string; // ID of item being interacted with
}

export interface GiftItem extends BaseItem {
  category: ItemCategory.GIFTS;
  type: GiftType;
  isOpened: boolean;
  assignedTo?: string; // ID of person this gift is for
}

export interface DecorationItem extends BaseItem {
  category: ItemCategory.DECORATIONS;
  type: DecorationType;
  isActive: boolean; // For lights, candles, etc.
  attachedTo?: string; // For ornaments on tree, lights on wall, etc.
}

export interface ComfortItem extends BaseItem {
  category: ItemCategory.COMFORT;
  type: ComfortType;
  isActive: boolean; // For fireplace, music, etc.
  temperature?: number; // For warmth-generating items
}

export interface TraditionItem extends BaseItem {
  category: ItemCategory.TRADITIONS;
  type: TraditionType;
  isActive: boolean; // For movie playing, book being read, etc.
}

export type GameItem = PersonItem | GiftItem | DecorationItem | ComfortItem | TraditionItem;

export enum AnimationState {
  IDLE = 'idle',
  HAPPY = 'happy',
  EXCITED = 'excited',
  TALKING = 'talking',
  WATCHING = 'watching',
  OPENING_GIFT = 'opening_gift',
  READING = 'reading',
  DRINKING = 'drinking',
  GIVING = 'giving',
  RECEIVING = 'receiving',
  NOSTALGIC = 'nostalgic',
  PEACEFUL = 'peaceful',
}

export interface ItemDefinition {
  category: ItemCategory;
  type: ItemType;
  name: string;
  description: string;
  icon: string; // emoji or icon identifier
  color: string; // category color
}

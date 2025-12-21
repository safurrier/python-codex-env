import { GameItem, ItemDefinition } from './items';
import { Interaction } from './interactions';

export interface GameState {
  items: GameItem[];
  interactions: Interaction[];
  connectionEnergy: number; // 0-100
  energyLevel: EnergyLevel;
  timeOfDay: TimeOfDay;
  roomTemperature: number; // visual warmth
  musicPlaying: boolean;
  fireplaceLit: boolean;
  endgameTriggered: boolean;
}

export enum EnergyLevel {
  EMPTY = 'empty',           // 0-10%
  DECORATED = 'decorated',   // 10-30%
  INHABITED = 'inhabited',   // 30-50%
  CONNECTED = 'connected',   // 50-75%
  MAGIC = 'magic',          // 75-100%
}

export enum TimeOfDay {
  DAWN = 'dawn',           // Blue-grey morning light
  MORNING = 'morning',     // Golden light
  AFTERNOON = 'afternoon', // Warm afternoon light
}

export interface PaletteCategory {
  name: string;
  color: string;
  items: ItemDefinition[];
}

export interface DragItem {
  itemDefinition: ItemDefinition;
  existingItemId?: string; // If dragging an existing item to move it
}

export interface DropResult {
  position: {
    x: number;
    y: number;
  };
}

export interface SavedScene {
  timestamp: number;
  items: GameItem[];
  connectionEnergy: number;
  screenshot?: string; // base64 image
}

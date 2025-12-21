import React, { useState, useEffect, useCallback } from 'react';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { TouchBackend } from 'react-dnd-touch-backend';
import Room from './components/Room';
import ItemPalette from './components/ItemPalette';
import {
  GameItem,
  ItemCategory,
  PersonType,
  GiftItem,
  DecorationItem,
  ComfortItem,
  TraditionItem,
  PersonItem,
  AnimationState,
  ItemDefinition,
} from './types/items';
import { GameState, TimeOfDay, EnergyLevel } from './types/game';
import { InteractionSystem } from './systems/InteractionSystem';
import { EnergySystem } from './systems/EnergySystem';
import './App.css';

const App: React.FC = () => {
  const [gameState, setGameState] = useState<GameState>({
    items: [],
    interactions: [],
    connectionEnergy: 0,
    energyLevel: EnergyLevel.EMPTY,
    timeOfDay: TimeOfDay.DAWN,
    roomTemperature: 0,
    musicPlaying: false,
    fireplaceLit: false,
    endgameTriggered: false,
  });

  const [interactionSystem] = useState(() => new InteractionSystem());
  const [energySystem] = useState(() => new EnergySystem());
  const [nextId, setNextId] = useState(1);

  const triggerEndgame = useCallback(() => {
    setGameState(prev => ({ ...prev, endgameTriggered: true }));

    // Show endgame message with enhanced sequence
    const message = document.createElement('div');
    message.className = 'endgame-message';
    message.innerHTML = `
      <div class="endgame-content">
        <h1>✨ Christmas Magic Achieved ✨</h1>
        <p class="endgame-reveal">You've built your perfect Christmas morning.</p>
        <p class="endgame-teaching">The magic wasn't in the gifts or decorations...</p>
        <p class="endgame-truth">It was in the connections you created.</p>
        <p class="endgame-final">This moment. This is what you'll remember.</p>
        <div class="endgame-stats">
          <div>Items placed: ${gameState.items.length}</div>
          <div>Connections made: ${gameState.interactions.length}</div>
          <div>Energy reached: 100%</div>
        </div>
      </div>
    `;
    document.body.appendChild(message);

    // Fade in with staggered text
    setTimeout(() => {
      message.style.opacity = '1';
    }, 100);

    // Add zoom-out effect to room
    const room = document.querySelector('.room') as HTMLElement;
    if (room) {
      setTimeout(() => {
        room.style.transform = 'scale(0.95)';
        room.style.filter = 'brightness(1.1) saturate(1.2)';
      }, 2000);
    }
  }, [gameState.items.length, gameState.interactions.length]);

  // Update interactions and energy whenever items change
  useEffect(() => {
    const interactions = interactionSystem.detectInteractions(gameState.items);
    const energy = energySystem.calculateEnergy(interactions);
    const energyLevel = energySystem.getEnergyLevel(energy);
    const updatedItems = interactionSystem.updateAnimations(gameState.items, interactions);

    // Update time of day based on energy
    let timeOfDay = TimeOfDay.DAWN;
    if (energy >= 30) timeOfDay = TimeOfDay.MORNING;
    if (energy >= 70) timeOfDay = TimeOfDay.AFTERNOON;

    setGameState(prev => ({
      ...prev,
      items: updatedItems,
      interactions,
      connectionEnergy: energy,
      energyLevel,
      timeOfDay,
    }));

    // Trigger endgame at 100% energy
    if (energy >= 100 && !gameState.endgameTriggered) {
      setTimeout(() => {
        triggerEndgame();
      }, 1000);
    }
  }, [gameState.items, gameState.endgameTriggered, interactionSystem, energySystem, triggerEndgame]);

  const handleItemDrop = useCallback((itemDefinition: ItemDefinition, position: { x: number; y: number }) => {
    const newItem = createItemFromDefinition(itemDefinition, position, nextId);
    setNextId(nextId + 1);

    setGameState(prev => ({
      ...prev,
      items: [...prev.items, newItem],
    }));
  }, [nextId]);

  const createItemFromDefinition = (
    def: ItemDefinition,
    position: { x: number; y: number },
    id: number
  ): GameItem => {
    const baseItem = {
      id: `item_${id}`,
      category: def.category,
      type: def.type,
      position,
      zIndex: id,
    };

    switch (def.category) {
      case ItemCategory.PEOPLE:
        return {
          ...baseItem,
          category: ItemCategory.PEOPLE,
          type: def.type as PersonType,
          animationState: AnimationState.IDLE,
        } as PersonItem;

      case ItemCategory.GIFTS:
        return {
          ...baseItem,
          category: ItemCategory.GIFTS,
          isOpened: false,
        } as GiftItem;

      case ItemCategory.DECORATIONS:
        return {
          ...baseItem,
          category: ItemCategory.DECORATIONS,
          isActive: false,
        } as DecorationItem;

      case ItemCategory.COMFORT:
        return {
          ...baseItem,
          category: ItemCategory.COMFORT,
          isActive: false,
          temperature: 0,
        } as ComfortItem;

      case ItemCategory.TRADITIONS:
        return {
          ...baseItem,
          category: ItemCategory.TRADITIONS,
          isActive: false,
        } as TraditionItem;

      default:
        return baseItem as GameItem;
    }
  };

  const handleItemClick = useCallback((itemId: string) => {
    setGameState(prev => {
      const updatedItems = prev.items.map(item => {
        if (item.id !== itemId) return item;

        // Handle click on people - they wave/smile
        if (item.category === ItemCategory.PEOPLE) {
          const personItem = item as PersonItem;
          const newState = { ...personItem, animationState: AnimationState.HAPPY } as PersonItem;

          // Reset animation after 2 seconds
          setTimeout(() => {
            setGameState(current => ({
              ...current,
              items: current.items.map(i =>
                i.id === itemId && i.category === ItemCategory.PEOPLE
                  ? { ...i, animationState: AnimationState.IDLE } as PersonItem
                  : i
              ),
            }));
          }, 2000);

          return newState;
        }

        // Handle different click interactions
        if (item.category === ItemCategory.GIFTS) {
          const giftItem = item as GiftItem;
          // Check if a person is nearby
          const nearbyPerson = prev.items.find(
            otherItem =>
              otherItem.category === ItemCategory.PEOPLE &&
              interactionSystem.calculateDistance(item.position, otherItem.position) < 150
          );

          if (nearbyPerson && !giftItem.isOpened) {
            return { ...giftItem, isOpened: true };
          }
        }

        if (item.category === ItemCategory.COMFORT) {
          const comfortItem = item as ComfortItem;
          if (comfortItem.type === 'fireplace') {
            return { ...comfortItem, isActive: !comfortItem.isActive };
          }
          if (comfortItem.type === 'music_player') {
            return { ...comfortItem, isActive: !comfortItem.isActive };
          }
        }

        if (item.category === ItemCategory.DECORATIONS) {
          const decorationItem = item as DecorationItem;
          if (decorationItem.type === 'candle') {
            return { ...decorationItem, isActive: !decorationItem.isActive };
          }
        }

        if (item.category === ItemCategory.TRADITIONS) {
          const traditionItem = item as TraditionItem;
          return { ...traditionItem, isActive: !traditionItem.isActive };
        }

        return item;
      });

      return { ...prev, items: updatedItems };
    });
  }, [interactionSystem]);

  const energyVisuals = energySystem.getEnergyVisuals(gameState.energyLevel);

  // Use TouchBackend on touch devices, HTML5Backend on desktop
  const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  const backend = isTouchDevice ? TouchBackend : HTML5Backend;

  return (
    <DndProvider backend={backend}>
      <div className="app">
        <ItemPalette connectionEnergy={gameState.connectionEnergy} />
        <div className="room-container">
          <Room
            items={gameState.items}
            energyLevel={gameState.energyLevel}
            timeOfDay={gameState.timeOfDay}
            frostOpacity={energyVisuals.frostOpacity}
            onItemDrop={handleItemDrop}
            onItemClick={handleItemClick}
          />
        </div>
      </div>
    </DndProvider>
  );
};

export default App;

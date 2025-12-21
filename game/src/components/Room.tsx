import React, { useCallback } from 'react';
import { useDrop } from 'react-dnd';
import { GameItem } from '../types/items';
import { EnergyLevel, TimeOfDay, DragItem } from '../types/game';
import Item from './Item';
import './Room.css';

interface RoomProps {
  items: GameItem[];
  energyLevel: EnergyLevel;
  timeOfDay: TimeOfDay;
  frostOpacity: number;
  onItemDrop: (itemDefinition: DragItem['itemDefinition'], position: { x: number; y: number }) => void;
  onItemClick: (itemId: string) => void;
}

const Room: React.FC<RoomProps> = ({
  items,
  energyLevel,
  timeOfDay,
  frostOpacity,
  onItemDrop,
  onItemClick,
}) => {
  const [, drop] = useDrop(() => ({
    accept: 'ITEM',
    drop: (item: DragItem, monitor) => {
      const offset = monitor.getClientOffset();
      if (offset) {
        // Account for palette width
        const roomElement = document.getElementById('room');
        if (roomElement) {
          const rect = roomElement.getBoundingClientRect();
          onItemDrop(item.itemDefinition, {
            x: offset.x - rect.left,
            y: offset.y - rect.top,
          });
        }
      }
    },
  }), [onItemDrop]);

  const getBackgroundColor = useCallback(() => {
    switch (energyLevel) {
      case EnergyLevel.EMPTY:
        return 'linear-gradient(to bottom, #4a5568 0%, #718096 100%)';
      case EnergyLevel.DECORATED:
        return 'linear-gradient(to bottom, #5a6578 0%, #8190a6 100%)';
      case EnergyLevel.INHABITED:
        return 'linear-gradient(to bottom, #7a8598 0%, #a1b0c6 100%)';
      case EnergyLevel.CONNECTED:
        return 'linear-gradient(to bottom, #c8a882 0%, #e8d8b8 100%)';
      case EnergyLevel.MAGIC:
        return 'linear-gradient(to bottom, #ffd700 0%, #ffed4e 100%)';
      default:
        return 'linear-gradient(to bottom, #4a5568 0%, #718096 100%)';
    }
  }, [energyLevel]);

  const getTimeFilter = useCallback(() => {
    switch (timeOfDay) {
      case TimeOfDay.DAWN:
        return 'brightness(0.7) saturate(0.8)';
      case TimeOfDay.MORNING:
        return 'brightness(1) saturate(1)';
      case TimeOfDay.AFTERNOON:
        return 'brightness(0.9) saturate(1.1)';
      default:
        return 'none';
    }
  }, [timeOfDay]);

  return (
    <div
      id="room"
      ref={drop}
      className="room"
      style={{
        background: getBackgroundColor(),
        filter: getTimeFilter(),
      }}
    >
      {/* Window with frost */}
      <div className="window">
        <div className="snow-outside"></div>
        <div
          className="frost"
          style={{ opacity: frostOpacity }}
        ></div>
      </div>

      {/* Furniture */}
      <div className="couch"></div>
      <div className="coffee-table"></div>
      <div className="armchair"></div>

      {/* Items */}
      {items.map((item) => (
        <Item
          key={item.id}
          item={item}
          onClick={() => onItemClick(item.id)}
        />
      ))}

      {/* Opening text */}
      {items.length === 0 && (
        <div className="opening-text">
          Build your Christmas morning…
        </div>
      )}
    </div>
  );
};

export default Room;

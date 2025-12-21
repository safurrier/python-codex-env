import React, { useState } from 'react';
import { useDrag } from 'react-dnd';
import { ItemDefinition } from '../types/items';
import { PALETTE_CATEGORIES } from '../data/itemDefinitions';
import { DragItem } from '../types/game';
import './ItemPalette.css';

interface PaletteItemProps {
  itemDefinition: ItemDefinition;
}

const PaletteItem: React.FC<PaletteItemProps> = ({ itemDefinition }) => {
  const [{ isDragging }, drag] = useDrag(() => ({
    type: 'ITEM',
    item: { itemDefinition } as DragItem,
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  }), [itemDefinition]);

  return (
    <div
      ref={drag}
      className="palette-item"
      style={{
        opacity: isDragging ? 0.5 : 1,
        borderColor: itemDefinition.color,
      }}
      title={itemDefinition.description}
    >
      <div className="palette-item-icon">{itemDefinition.icon}</div>
      <div className="palette-item-name">{itemDefinition.name}</div>
    </div>
  );
};

interface ItemPaletteProps {
  connectionEnergy: number;
}

const ItemPalette: React.FC<ItemPaletteProps> = ({ connectionEnergy }) => {
  const [expandedCategory, setExpandedCategory] = useState<string | null>('People');

  const toggleCategory = (categoryName: string) => {
    setExpandedCategory(expandedCategory === categoryName ? null : categoryName);
  };

  return (
    <div className="item-palette">
      <div className="palette-header">
        <h2>Items</h2>
        <div className="energy-meter">
          <div className="energy-label">Connection Energy</div>
          <div className="energy-bar">
            <div
              className="energy-fill"
              style={{
                width: `${connectionEnergy}%`,
                background: `linear-gradient(to right,
                  #FFB6C1 0%,
                  #FFD700 25%,
                  #FF6347 50%,
                  #8B0000 75%,
                  #FFD700 100%)`,
              }}
            ></div>
          </div>
          <div className="energy-value">{Math.round(connectionEnergy)}%</div>
        </div>
      </div>

      <div className="palette-categories">
        {PALETTE_CATEGORIES.map((category) => (
          <div key={category.name} className="palette-category">
            <div
              className="category-header"
              style={{ background: category.color }}
              onClick={() => toggleCategory(category.name)}
            >
              <span>{category.name}</span>
              <span className="category-toggle">
                {expandedCategory === category.name ? '▼' : '▶'}
              </span>
            </div>

            {expandedCategory === category.name && (
              <div className="category-items">
                {category.items.map((item) => (
                  <PaletteItem key={`${item.category}_${item.type}`} itemDefinition={item} />
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ItemPalette;

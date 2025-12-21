import React from 'react';
import { GameItem, ItemCategory, PersonItem, GiftItem, DecorationItem, ComfortItem, TraditionItem } from '../types/items';
import './Item.css';

interface ItemProps {
  item: GameItem;
  onClick: () => void;
}

const Item: React.FC<ItemProps> = ({ item, onClick }) => {
  const getItemEmoji = (): string => {
    switch (item.category) {
      case ItemCategory.PEOPLE: {
        const personItem = item as PersonItem;
        switch (personItem.type) {
          case 'child': return '🧒';
          case 'parent': return '👨';
          case 'grandparent': return '👴';
          case 'teen': return '🧑';
          case 'pet': return '🐕';
          case 'partner': return '👫';
          default: return '👤';
        }
      }
      case ItemCategory.GIFTS: {
        const giftItem = item as GiftItem;
        if (giftItem.isOpened) return '🎊';
        switch (giftItem.type) {
          case 'small_box': return '🎁';
          case 'medium_box': return '📦';
          case 'large_box': return '🎀';
          case 'gift_bag': return '🛍️';
          case 'stocking': return '🧦';
          case 'handmade': return '🎨';
          case 'practical': return '👔';
          case 'experience': return '🎫';
          default: return '🎁';
        }
      }
      case ItemCategory.DECORATIONS: {
        const decorationItem = item as DecorationItem;
        switch (decorationItem.type) {
          case 'tree': return '🎄';
          case 'ornament': return '🔴';
          case 'heirloom_ornament': return '⭐';
          case 'handmade_ornament': return '🌟';
          case 'string_lights': return '💡';
          case 'wall_stocking': return '🧦';
          case 'wreath': return '🌿';
          case 'garland': return '🎋';
          case 'candle': return decorationItem.isActive ? '🕯️' : '🕯';
          case 'tree_topper': return '⭐';
          default: return '🎄';
        }
      }
      case ItemCategory.COMFORT: {
        const comfortItem = item as ComfortItem;
        switch (comfortItem.type) {
          case 'fireplace': return comfortItem.isActive ? '🔥' : '🪵';
          case 'hot_cocoa': return '☕';
          case 'coffee': return '☕';
          case 'blanket': return '🛋️';
          case 'breakfast': return '🥐';
          case 'music_player': return comfortItem.isActive ? '🎵' : '🎵';
          case 'cookies': return '🍪';
          default: return '☕';
        }
      }
      case ItemCategory.TRADITIONS: {
        const traditionItem = item as TraditionItem;
        switch (traditionItem.type) {
          case 'photo_album': return '📸';
          case 'story_book': return '📖';
          case 'holiday_movie': return traditionItem.isActive ? '📺' : '📺';
          case 'advent_calendar': return '📅';
          case 'nativity_scene': return '🌟';
          case 'recipe_book': return '📗';
          case 'santa_letter': return '✉️';
          case 'christmas_cards': return '💌';
          default: return '📖';
        }
      }
      default:
        return '❓';
    }
  };

  const getItemClass = (): string => {
    const classes = ['item'];

    if (item.category === ItemCategory.PEOPLE) {
      const personItem = item as PersonItem;
      if (personItem.animationState === 'happy' || personItem.animationState === 'excited') {
        classes.push('glow');
      }
      if (personItem.interactionTarget) {
        classes.push('float');
      }
    }

    if (item.category === ItemCategory.DECORATIONS) {
      const decorationItem = item as DecorationItem;
      if (decorationItem.isActive) {
        classes.push('glow');
      }
    }

    return classes.join(' ');
  };

  return (
    <div
      className={getItemClass()}
      style={{
        position: 'absolute',
        left: item.position.x,
        top: item.position.y,
        zIndex: item.zIndex,
        fontSize: '48px',
        cursor: 'pointer',
        userSelect: 'none',
        transition: 'all 0.3s ease',
      }}
      onClick={onClick}
    >
      {getItemEmoji()}
    </div>
  );
};

export default Item;

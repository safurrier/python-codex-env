import { describe, it, expect, beforeEach } from 'vitest';
import { InteractionSystem } from '../InteractionSystem';
import { GameItem, ItemCategory, PersonType, GiftType, AnimationState } from '../../types/items';

describe('InteractionSystem', () => {
  let system: InteractionSystem;

  beforeEach(() => {
    system = new InteractionSystem();
  });

  it('should detect parent-child interaction when they are close', () => {
    const items: GameItem[] = [
      {
        id: 'parent1',
        category: ItemCategory.PEOPLE,
        type: PersonType.PARENT,
        position: { x: 100, y: 100 },
        zIndex: 1,
        animationState: AnimationState.IDLE,
      },
      {
        id: 'child1',
        category: ItemCategory.PEOPLE,
        type: PersonType.CHILD,
        position: { x: 150, y: 100 },
        zIndex: 2,
        animationState: AnimationState.IDLE,
      },
    ];

    const interactions = system.detectInteractions(items);
    expect(interactions.length).toBeGreaterThan(0);
    expect(interactions.some(i => i.type === 'parent_child')).toBe(true);
  });

  it('should not detect interaction when items are too far apart', () => {
    const items: GameItem[] = [
      {
        id: 'parent1',
        category: ItemCategory.PEOPLE,
        type: PersonType.PARENT,
        position: { x: 100, y: 100 },
        zIndex: 1,
        animationState: AnimationState.IDLE,
      },
      {
        id: 'child1',
        category: ItemCategory.PEOPLE,
        type: PersonType.CHILD,
        position: { x: 500, y: 500 },
        zIndex: 2,
        animationState: AnimationState.IDLE,
      },
    ];

    const interactions = system.detectInteractions(items);
    const parentChildInteractions = interactions.filter(i => i.type === 'parent_child');
    expect(parentChildInteractions.length).toBe(0);
  });

  it('should detect child-gift interaction', () => {
    const items: GameItem[] = [
      {
        id: 'child1',
        category: ItemCategory.PEOPLE,
        type: PersonType.CHILD,
        position: { x: 100, y: 100 },
        zIndex: 1,
        animationState: AnimationState.IDLE,
      },
      {
        id: 'gift1',
        category: ItemCategory.GIFTS,
        type: GiftType.SMALL_BOX,
        position: { x: 120, y: 100 },
        zIndex: 2,
        isOpened: false,
      },
    ];

    const interactions = system.detectInteractions(items);
    expect(interactions.some(i => i.type === 'child_gift')).toBe(true);
  });

  it('should calculate distance correctly', () => {
    const pos1 = { x: 0, y: 0 };
    const pos2 = { x: 3, y: 4 };
    const distance = system.calculateDistance(pos1, pos2);
    expect(distance).toBe(5);
  });

  it('should return same array reference when no animations change', () => {
    const items: GameItem[] = [
      {
        id: 'parent1',
        category: ItemCategory.PEOPLE,
        type: PersonType.PARENT,
        position: { x: 100, y: 100 },
        zIndex: 1,
        animationState: AnimationState.TALKING,
        interactionTarget: 'child1',
      },
    ];

    const interactions = [
      {
        id: 'int1',
        participants: ['parent1', 'child1'],
        type: 'parent_child' as const,
        energyValue: 15,
        isActive: true,
      },
    ];

    // updateAnimations should return the same reference if animation already matches
    const result = system.updateAnimations(items, interactions);
    expect(result).toBe(items); // Same reference
  });

  it('should return new array reference when animations change', () => {
    const items: GameItem[] = [
      {
        id: 'parent1',
        category: ItemCategory.PEOPLE,
        type: PersonType.PARENT,
        position: { x: 100, y: 100 },
        zIndex: 1,
        animationState: AnimationState.IDLE,
      },
    ];

    const interactions = [
      {
        id: 'int1',
        participants: ['parent1', 'child1'],
        type: 'parent_child' as const,
        energyValue: 15,
        isActive: true,
      },
    ];

    // updateAnimations should return a new reference if animation changes
    const result = system.updateAnimations(items, interactions);
    expect(result).not.toBe(items); // Different reference
    expect(result[0].animationState).toBe(AnimationState.TALKING);
  });
});

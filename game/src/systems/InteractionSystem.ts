import {
  GameItem,
  ItemCategory,
  PersonType,
  DecorationType,
  ComfortType,
  TraditionType,
  PersonItem,
  AnimationState,
} from '../types/items';
import {
  Interaction,
  InteractionType,
  InteractionRule,
  EffectType,
} from '../types/interactions';

export class InteractionSystem {
  private static readonly INTERACTION_DISTANCE = 150; // pixels
  private interactionRules: InteractionRule[];

  constructor() {
    this.interactionRules = this.initializeRules();
  }

  private initializeRules(): InteractionRule[] {
    return [
      // Person to Person interactions
      {
        type: InteractionType.PARENT_CHILD,
        requiredItems: [
          { type: PersonType.PARENT, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
          { type: PersonType.CHILD, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
        ],
        energyValue: 15,
        effects: [
          { type: EffectType.GLOW, intensity: 0.6 },
          { type: EffectType.WARMTH, intensity: 0.5 },
        ],
      },
      {
        type: InteractionType.GRANDPARENT_CHILD,
        requiredItems: [
          { type: PersonType.GRANDPARENT, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
          { type: PersonType.CHILD, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
        ],
        energyValue: 20,
        effects: [
          { type: EffectType.GLOW, intensity: 0.8 },
          { type: EffectType.WARMTH, intensity: 0.7 },
        ],
      },
      {
        type: InteractionType.PARTNERS,
        requiredItems: [
          { type: PersonType.PARTNER, minCount: 2, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
        ],
        energyValue: 12,
        effects: [
          { type: EffectType.GLOW, intensity: 0.5 },
        ],
      },
      {
        type: InteractionType.PET_PERSON,
        requiredItems: [
          { type: PersonType.PET, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
          { category: ItemCategory.PEOPLE, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
        ],
        energyValue: 10,
        effects: [
          { type: EffectType.SPARKLE, intensity: 0.6 },
        ],
      },
      // Person to Gift interactions
      {
        type: InteractionType.CHILD_GIFT,
        requiredItems: [
          { type: PersonType.CHILD, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
          { category: ItemCategory.GIFTS, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
        ],
        energyValue: 8,
        effects: [
          { type: EffectType.GLOW, intensity: 0.4 },
        ],
      },
      {
        type: InteractionType.ADULT_GIFT,
        requiredItems: [
          { type: PersonType.PARENT, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
          { category: ItemCategory.GIFTS, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
        ],
        energyValue: 5,
        effects: [
          { type: EffectType.GLOW, intensity: 0.3 },
        ],
      },
      // Person to Decoration interactions
      {
        type: InteractionType.FAMILY_TREE,
        requiredItems: [
          { type: DecorationType.TREE, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
          { category: ItemCategory.PEOPLE, minCount: 2, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
        ],
        energyValue: 18,
        effects: [
          { type: EffectType.GLOW, intensity: 0.7 },
          { type: EffectType.SPARKLE, intensity: 0.5 },
        ],
      },
      {
        type: InteractionType.HEIRLOOM_ORNAMENT,
        requiredItems: [
          { type: DecorationType.HEIRLOOM_ORNAMENT, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
          { type: PersonType.GRANDPARENT, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
        ],
        energyValue: 25,
        effects: [
          { type: EffectType.GLOW, intensity: 0.9 },
          { type: EffectType.FLASHBACK, intensity: 0.7, duration: 3000 },
        ],
      },
      // Person to Comfort interactions
      {
        type: InteractionType.FIREPLACE_GATHERING,
        requiredItems: [
          { type: ComfortType.FIREPLACE, minCount: 1, maxDistance: 200 },
          { category: ItemCategory.PEOPLE, minCount: 2, maxDistance: 200 },
        ],
        energyValue: 15,
        effects: [
          { type: EffectType.WARMTH, intensity: 0.8 },
          { type: EffectType.GLOW, intensity: 0.6 },
        ],
      },
      {
        type: InteractionType.COCOA_MOMENT,
        requiredItems: [
          { type: ComfortType.HOT_COCOA, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
          { category: ItemCategory.PEOPLE, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
        ],
        energyValue: 7,
        effects: [
          { type: EffectType.WARMTH, intensity: 0.4 },
        ],
      },
      {
        type: InteractionType.FAMILY_MEAL,
        requiredItems: [
          { type: ComfortType.BREAKFAST, minCount: 1, maxDistance: 200 },
          { category: ItemCategory.PEOPLE, minCount: 3, maxDistance: 200 },
        ],
        energyValue: 20,
        effects: [
          { type: EffectType.WARMTH, intensity: 0.7 },
          { type: EffectType.GLOW, intensity: 0.6 },
        ],
      },
      {
        type: InteractionType.MUSIC_ENJOYMENT,
        requiredItems: [
          { type: ComfortType.MUSIC_PLAYER, minCount: 1, maxDistance: 300 },
          { category: ItemCategory.PEOPLE, minCount: 1, maxDistance: 300 },
        ],
        energyValue: 8,
        effects: [
          { type: EffectType.SPARKLE, intensity: 0.4 },
        ],
      },
      // Person to Tradition interactions
      {
        type: InteractionType.STORYTELLING,
        requiredItems: [
          { type: TraditionType.STORY_BOOK, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
          { type: PersonType.PARENT, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
          { type: PersonType.CHILD, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
        ],
        energyValue: 22,
        effects: [
          { type: EffectType.GLOW, intensity: 0.8 },
          { type: EffectType.SACRED_FEELING, intensity: 0.5, duration: 5000 },
        ],
      },
      {
        type: InteractionType.PHOTO_SHARING,
        requiredItems: [
          { type: TraditionType.PHOTO_ALBUM, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
          { type: PersonType.GRANDPARENT, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
        ],
        energyValue: 20,
        effects: [
          { type: EffectType.FLASHBACK, intensity: 0.8, duration: 4000 },
          { type: EffectType.GLOW, intensity: 0.6 },
        ],
      },
      {
        type: InteractionType.MOVIE_WATCHING,
        requiredItems: [
          { type: TraditionType.HOLIDAY_MOVIE, minCount: 1, maxDistance: 250 },
          { category: ItemCategory.PEOPLE, minCount: 2, maxDistance: 250 },
        ],
        energyValue: 18,
        effects: [
          { type: EffectType.GLOW, intensity: 0.5 },
        ],
      },
      {
        type: InteractionType.SPIRITUAL_MOMENT,
        requiredItems: [
          { type: TraditionType.NATIVITY_SCENE, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
          { category: ItemCategory.PEOPLE, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
        ],
        energyValue: 15,
        effects: [
          { type: EffectType.SACRED_FEELING, intensity: 0.9, duration: 6000 },
        ],
      },
      // Easter Egg: Four Generations
      {
        type: InteractionType.FOUR_GENERATIONS,
        requiredItems: [
          { type: PersonType.CHILD, minCount: 1, maxDistance: 250 },
          { type: PersonType.PARENT, minCount: 1, maxDistance: 250 },
          { type: PersonType.GRANDPARENT, minCount: 1, maxDistance: 250 },
          { type: TraditionType.PHOTO_ALBUM, minCount: 1, maxDistance: 250 },
        ],
        energyValue: 50,
        effects: [
          { type: EffectType.SNOW_INSIDE, intensity: 1.0, duration: 5000 },
          { type: EffectType.GLOW, intensity: 1.0 },
        ],
      },
      // Easter Egg: Pet's Christmas
      {
        type: InteractionType.PET_GIFT,
        requiredItems: [
          { type: PersonType.PET, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
          { category: ItemCategory.GIFTS, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
        ],
        energyValue: 30,
        effects: [
          { type: EffectType.SPARKLE, intensity: 1.0 },
          { type: EffectType.GLOW, intensity: 0.9 },
        ],
      },
      // Easter Egg: Quiet Moment
      {
        type: InteractionType.QUIET_MOMENT,
        requiredItems: [
          { category: ItemCategory.PEOPLE, minCount: 2, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
          { type: ComfortType.HOT_COCOA, minCount: 2, maxDistance: 200 },
          { type: ComfortType.FIREPLACE, minCount: 1, maxDistance: 200 },
          { type: ComfortType.MUSIC_PLAYER, minCount: 1, maxDistance: 300 },
        ],
        energyValue: 40,
        effects: [
          { type: EffectType.FADE_OTHERS, intensity: 0.7, duration: 8000 },
          { type: EffectType.GLOW, intensity: 1.0 },
        ],
      },
      // Easter Egg: Handmade Treasure
      {
        type: InteractionType.HANDMADE_TREASURE,
        requiredItems: [
          { type: DecorationType.HANDMADE_ORNAMENT, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
          { type: DecorationType.TREE, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
          { type: PersonType.CHILD, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
          { type: PersonType.GRANDPARENT, minCount: 1, maxDistance: InteractionSystem.INTERACTION_DISTANCE },
        ],
        energyValue: 45,
        effects: [
          { type: EffectType.FLASHBACK, intensity: 1.0, duration: 6000 },
          { type: EffectType.GLOW, intensity: 0.95 },
        ],
      },
    ];
  }

  public detectInteractions(items: GameItem[]): Interaction[] {
    const interactions: Interaction[] = [];

    for (const rule of this.interactionRules) {
      const matchingItems = this.findMatchingItems(items, rule);

      if (matchingItems.length > 0) {
        const interaction: Interaction = {
          id: `${rule.type}_${Date.now()}_${Math.random()}`,
          participants: matchingItems.map(item => item.id),
          type: rule.type,
          energyValue: rule.energyValue,
          isActive: true,
        };

        interactions.push(interaction);
      }
    }

    return interactions;
  }

  private findMatchingItems(items: GameItem[], rule: InteractionRule): GameItem[] {
    const matches: GameItem[] = [];

    for (const requirement of rule.requiredItems) {
      const matchingForRequirement = items.filter(item => {
        if (requirement.type && item.type !== requirement.type) {
          return false;
        }
        if (requirement.category && item.category !== requirement.category) {
          return false;
        }
        return true;
      });

      if (requirement.minCount && matchingForRequirement.length < requirement.minCount) {
        return []; // Rule not satisfied
      }

      matches.push(...matchingForRequirement.slice(0, requirement.minCount || matchingForRequirement.length));
    }

    // Check distance constraints
    if (matches.length > 1 && rule.requiredItems[0].maxDistance) {
      const maxDistance = rule.requiredItems[0].maxDistance;
      const first = matches[0];

      for (let i = 1; i < matches.length; i++) {
        const distance = this.calculateDistance(first.position, matches[i].position);
        if (distance > maxDistance) {
          return []; // Items too far apart
        }
      }
    }

    return matches;
  }

  public calculateDistance(pos1: { x: number; y: number }, pos2: { x: number; y: number }): number {
    const dx = pos1.x - pos2.x;
    const dy = pos1.y - pos2.y;
    return Math.sqrt(dx * dx + dy * dy);
  }

  public updateAnimations(items: GameItem[], interactions: Interaction[]): GameItem[] {
    const updatedItems = [...items];

    for (const interaction of interactions) {
      for (const itemId of interaction.participants) {
        const itemIndex = updatedItems.findIndex(item => item.id === itemId);
        if (itemIndex !== -1 && updatedItems[itemIndex].category === ItemCategory.PEOPLE) {
          const personItem = updatedItems[itemIndex] as PersonItem;

          // Update animation state based on interaction type
          const newState = this.getAnimationForInteraction(interaction.type, personItem.type);
          updatedItems[itemIndex] = {
            ...personItem,
            animationState: newState,
            interactionTarget: interaction.participants.find(id => id !== itemId),
          };
        }
      }
    }

    return updatedItems;
  }

  private getAnimationForInteraction(interactionType: InteractionType, personType: PersonType): AnimationState {
    switch (interactionType) {
      case InteractionType.PARENT_CHILD:
      case InteractionType.GRANDPARENT_CHILD:
        return AnimationState.TALKING;
      case InteractionType.STORYTELLING:
        return AnimationState.READING;
      case InteractionType.PHOTO_SHARING:
        return AnimationState.NOSTALGIC;
      case InteractionType.COCOA_MOMENT:
        return AnimationState.DRINKING;
      case InteractionType.CHILD_GIFT:
        if (personType === PersonType.CHILD) {
          return AnimationState.EXCITED;
        }
        return AnimationState.HAPPY;
      case InteractionType.FIREPLACE_GATHERING:
      case InteractionType.QUIET_MOMENT:
        return AnimationState.PEACEFUL;
      default:
        return AnimationState.HAPPY;
    }
  }

  public getInteractionRule(type: InteractionType): InteractionRule | undefined {
    return this.interactionRules.find(rule => rule.type === type);
  }
}

import { describe, it, expect, beforeEach } from 'vitest';
import { EnergySystem } from '../EnergySystem';
import { EnergyLevel } from '../../types/game';
import { Interaction, InteractionType } from '../../types/interactions';

describe('EnergySystem', () => {
  let system: EnergySystem;

  beforeEach(() => {
    system = new EnergySystem();
  });

  it('should start with zero energy', () => {
    expect(system.getEnergy()).toBe(0);
  });

  it('should increase energy when interactions are added', () => {
    const interactions: Interaction[] = [
      {
        id: 'int1',
        participants: ['item1', 'item2'],
        type: InteractionType.PARENT_CHILD,
        energyValue: 15,
        isActive: true,
      },
    ];

    const energy = system.calculateEnergy(interactions);
    expect(energy).toBe(15);
  });

  it('should not double-count the same interaction', () => {
    const interactions: Interaction[] = [
      {
        id: 'int1',
        participants: ['item1', 'item2'],
        type: InteractionType.PARENT_CHILD,
        energyValue: 15,
        isActive: true,
      },
    ];

    system.calculateEnergy(interactions);
    const energy = system.calculateEnergy(interactions); // Same interaction again
    expect(energy).toBe(15); // Should still be 15, not 30
  });

  it('should return correct energy level for different energy values', () => {
    expect(system.getEnergyLevel(5)).toBe(EnergyLevel.EMPTY);
    expect(system.getEnergyLevel(15)).toBe(EnergyLevel.DECORATED);
    expect(system.getEnergyLevel(35)).toBe(EnergyLevel.INHABITED);
    expect(system.getEnergyLevel(55)).toBe(EnergyLevel.CONNECTED);
    expect(system.getEnergyLevel(80)).toBe(EnergyLevel.MAGIC);
  });

  it('should cap energy at 100', () => {
    system.setEnergy(150);
    expect(system.getEnergy()).toBe(100);
  });

  it('should not allow negative energy', () => {
    system.setEnergy(-10);
    expect(system.getEnergy()).toBe(0);
  });

  it('should reset energy and interactions', () => {
    system.setEnergy(50);
    system.reset();
    expect(system.getEnergy()).toBe(0);
  });

  it('should provide visual properties for each energy level', () => {
    const visuals = system.getEnergyVisuals(EnergyLevel.MAGIC);
    expect(visuals.frostOpacity).toBe(0);
    expect(visuals.brightness).toBe(1.0);
  });
});

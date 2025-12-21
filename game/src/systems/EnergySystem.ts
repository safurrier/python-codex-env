import { Interaction } from '../types/interactions';
import { EnergyLevel } from '../types/game';

export class EnergySystem {
  private energy: number = 0;
  private maxEnergy: number = 100;
  private activeInteractions: Set<string> = new Set();

  public calculateEnergy(interactions: Interaction[]): number {
    // Track which interactions are new vs. ongoing
    const currentInteractionIds = new Set(interactions.map(i => this.getInteractionSignature(i)));

    // Add energy for new interactions
    for (const interaction of interactions) {
      const signature = this.getInteractionSignature(interaction);

      if (!this.activeInteractions.has(signature)) {
        // New interaction - add energy
        this.energy = Math.min(this.maxEnergy, this.energy + interaction.energyValue);
        this.activeInteractions.add(signature);
      }
    }

    // Remove expired interactions
    for (const signature of this.activeInteractions) {
      if (!currentInteractionIds.has(signature)) {
        this.activeInteractions.delete(signature);
      }
    }

    // Slowly decay energy if no interactions
    if (interactions.length === 0 && this.energy > 0) {
      this.energy = Math.max(0, this.energy - 0.1);
    }

    return this.energy;
  }

  public getEnergyLevel(energy: number): EnergyLevel {
    if (energy >= 75) return EnergyLevel.MAGIC;
    if (energy >= 50) return EnergyLevel.CONNECTED;
    if (energy >= 30) return EnergyLevel.INHABITED;
    if (energy >= 10) return EnergyLevel.DECORATED;
    return EnergyLevel.EMPTY;
  }

  public getEnergy(): number {
    return this.energy;
  }

  public setEnergy(value: number): void {
    this.energy = Math.max(0, Math.min(this.maxEnergy, value));
  }

  public reset(): void {
    this.energy = 0;
    this.activeInteractions.clear();
  }

  // Create a unique signature for an interaction to track if it's new or ongoing
  private getInteractionSignature(interaction: Interaction): string {
    const sortedParticipants = [...interaction.participants].sort();
    return `${interaction.type}_${sortedParticipants.join('_')}`;
  }

  // Get visual properties based on energy level
  public getEnergyVisuals(energyLevel: EnergyLevel): {
    lightTemperature: string;
    saturation: number;
    brightness: number;
    frostOpacity: number;
  } {
    switch (energyLevel) {
      case EnergyLevel.EMPTY:
        return {
          lightTemperature: '#B0C4DE', // Cool blue-grey
          saturation: 0.7,
          brightness: 0.8,
          frostOpacity: 1.0,
        };
      case EnergyLevel.DECORATED:
        return {
          lightTemperature: '#C8D8E8', // Slightly warmer
          saturation: 0.8,
          brightness: 0.85,
          frostOpacity: 0.8,
        };
      case EnergyLevel.INHABITED:
        return {
          lightTemperature: '#E8D8C8', // Warm
          saturation: 0.9,
          brightness: 0.9,
          frostOpacity: 0.5,
        };
      case EnergyLevel.CONNECTED:
        return {
          lightTemperature: '#F5DEB3', // Golden
          saturation: 1.0,
          brightness: 0.95,
          frostOpacity: 0.2,
        };
      case EnergyLevel.MAGIC:
        return {
          lightTemperature: '#FFD700', // Rich golden
          saturation: 1.1,
          brightness: 1.0,
          frostOpacity: 0.0,
        };
    }
  }
}

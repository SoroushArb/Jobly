/**
 * Adapter factory and detector
 * Tries all adapters and selects the best match
 */
import { Page } from 'playwright';
import { ATSAdapter, DetectionResult } from './base';
import { GreenhouseAdapter } from './greenhouse';
import { LeverAdapter } from './lever';
import { WorkdayAdapter } from './workday';
import { LinkedInAdapter } from './linkedin';
import { GenericAdapter } from './generic';

export class AdapterFactory {
  private adapters: ATSAdapter[];

  constructor() {
    this.adapters = [
      new GreenhouseAdapter(),
      new LeverAdapter(),
      new WorkdayAdapter(),
      new LinkedInAdapter(),
      new GenericAdapter(), // Always last as fallback
    ];
  }

  /**
   * Detect the best adapter for the current page
   */
  async detectAdapter(page: Page): Promise<{ adapter: ATSAdapter; detection: DetectionResult }> {
    let bestAdapter: ATSAdapter = this.adapters[this.adapters.length - 1]; // Default to generic
    let bestDetection: DetectionResult = {
      ats_type: 'generic',
      confidence: 0,
      indicators: [],
    };

    // Try all adapters
    for (const adapter of this.adapters) {
      try {
        const detection = await adapter.detect(page);
        
        console.log(`Adapter ${detection.ats_type}: confidence=${detection.confidence}`);

        if (detection.confidence > bestDetection.confidence) {
          bestDetection = detection;
          bestAdapter = adapter;
        }
      } catch (error) {
        console.error(`Error detecting with adapter:`, error);
      }
    }

    console.log(`Selected adapter: ${bestDetection.ats_type} (confidence: ${bestDetection.confidence})`);

    return { adapter: bestAdapter, detection: bestDetection };
  }

  /**
   * Get adapter by type name
   */
  getAdapterByType(atsType: string): ATSAdapter | null {
    const adapterMap: Record<string, ATSAdapter> = {
      greenhouse: new GreenhouseAdapter(),
      lever: new LeverAdapter(),
      workday: new WorkdayAdapter(),
      linkedin: new LinkedInAdapter(),
      generic: new GenericAdapter(),
    };

    return adapterMap[atsType] || null;
  }
}

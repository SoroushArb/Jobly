/**
 * Greenhouse ATS Adapter
 */
import { Page } from 'playwright';
import { ATSAdapter, DetectionResult, FieldMapping, FillResult } from './base';

export class GreenhouseAdapter extends ATSAdapter {
  async detect(page: Page): Promise<DetectionResult> {
    const indicators: string[] = [];
    let confidence = 0;

    // Check for Greenhouse-specific elements
    const hasGreenhouseBranding = await page.locator('a[href*="greenhouse.io"]').count() > 0;
    if (hasGreenhouseBranding) {
      indicators.push('greenhouse.io link found');
      confidence += 0.4;
    }

    // Check for Greenhouse form structure
    const hasApplicationForm = await page.locator('#application_form').count() > 0;
    if (hasApplicationForm) {
      indicators.push('Greenhouse application form ID');
      confidence += 0.4;
    }

    // Check URL patterns
    const url = page.url();
    if (url.includes('boards.greenhouse.io') || url.includes('grnh.se')) {
      indicators.push('Greenhouse URL pattern');
      confidence += 0.3;
    }

    // Check for specific field patterns
    const hasJobAppFields = await page.locator('[id^="job_application_"]').count() > 0;
    if (hasJobAppFields) {
      indicators.push('Greenhouse field naming convention');
      confidence += 0.2;
    }

    return {
      ats_type: 'greenhouse',
      confidence: Math.min(confidence, 1.0),
      indicators,
    };
  }

  async collectFields(page: Page): Promise<FieldMapping[]> {
    const mappings: FieldMapping[] = [];

    // Common Greenhouse field patterns
    const fieldPatterns = [
      { canonical: 'name', selectors: ['#first_name', '[name="job_application[first_name]"]'] },
      { canonical: 'surname', selectors: ['#last_name', '[name="job_application[last_name]"]'] },
      { canonical: 'email', selectors: ['#email', '[name="job_application[email]"]'] },
      { canonical: 'phone', selectors: ['#phone', '[name="job_application[phone]"]'] },
      { canonical: 'resume', selectors: ['#resume', 'input[type="file"][name*="resume"]'] },
      { canonical: 'linkedin', selectors: ['[name*="linkedin"]', '#linkedin'] },
    ];

    for (const pattern of fieldPatterns) {
      for (const selector of pattern.selectors) {
        const element = page.locator(selector).first();
        if (await element.count() > 0) {
          const tagName = await element.evaluate((el) => el.tagName.toLowerCase());
          const type = await element.evaluate((el) => 
            el.tagName.toLowerCase() === 'select' ? 'select' :
            el.tagName.toLowerCase() === 'textarea' ? 'textarea' :
            (el as HTMLInputElement).type || 'input'
          );

          mappings.push({
            canonical_field: pattern.canonical,
            selector,
            type: type === 'file' ? 'input' : type as any,
            label: pattern.canonical,
          });
          break;
        }
      }
    }

    return mappings;
  }

  async fill(page: Page, data: Record<string, any>): Promise<FillResult[]> {
    const results: FillResult[] = [];

    // Map canonical fields to Greenhouse selectors
    const fieldMap: Record<string, string> = {
      name: '#first_name',
      surname: '#last_name',
      email: '#email',
      phone: '#phone',
      linkedin: '[name*="linkedin"]',
      github: '[name*="github"]',
    };

    for (const [canonicalField, value] of Object.entries(data)) {
      const selector = fieldMap[canonicalField];
      if (!selector) {
        results.push({
          field_name: canonicalField,
          value: String(value),
          success: false,
          error: 'No selector mapping found',
        });
        continue;
      }

      try {
        const element = page.locator(selector).first();
        const count = await element.count();

        if (count === 0) {
          results.push({
            field_name: canonicalField,
            value: String(value),
            success: false,
            error: 'Field not found on page',
          });
          continue;
        }

        // Fill the field
        await element.fill(String(value));
        await page.waitForTimeout(100); // Small delay for stability

        results.push({
          field_name: canonicalField,
          value: String(value),
          success: true,
        });
      } catch (error) {
        results.push({
          field_name: canonicalField,
          value: String(value),
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error',
        });
      }
    }

    return results;
  }

  async attachResume(page: Page, filepath: string): Promise<boolean> {
    try {
      // Try common Greenhouse resume upload selectors
      const selectors = [
        '#resume',
        'input[type="file"][name*="resume"]',
        '[name="job_application[resume]"]',
      ];

      for (const selector of selectors) {
        const element = page.locator(selector).first();
        if (await element.count() > 0) {
          await element.setInputFiles(filepath);
          await page.waitForTimeout(500); // Wait for upload to process
          return true;
        }
      }

      return false;
    } catch (error) {
      console.error('Failed to attach resume:', error);
      return false;
    }
  }
}

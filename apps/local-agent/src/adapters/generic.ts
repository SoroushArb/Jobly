/**
 * Generic fallback adapter for unknown ATS or custom forms
 */
import { Page } from 'playwright';
import { ATSAdapter, DetectionResult, FieldMapping, FillResult } from './base';

export class GenericAdapter extends ATSAdapter {
  async detect(page: Page): Promise<DetectionResult> {
    // Generic adapter always returns low confidence
    // It's used as a fallback when no specific ATS is detected
    return {
      ats_type: 'generic',
      confidence: 0.1,
      indicators: ['Fallback generic adapter'],
    };
  }

  async collectFields(page: Page): Promise<FieldMapping[]> {
    const mappings: FieldMapping[] = [];

    // Try to find common form fields by multiple strategies
    const commonFields = [
      {
        canonical: 'name',
        labels: ['First Name', 'Name', 'Full Name', 'Your Name'],
      },
      {
        canonical: 'surname',
        labels: ['Last Name', 'Surname', 'Family Name'],
      },
      {
        canonical: 'email',
        labels: ['Email', 'Email Address', 'E-mail'],
      },
      {
        canonical: 'phone',
        labels: ['Phone', 'Phone Number', 'Telephone', 'Mobile'],
      },
      {
        canonical: 'linkedin',
        labels: ['LinkedIn', 'LinkedIn URL', 'LinkedIn Profile'],
      },
      {
        canonical: 'github',
        labels: ['GitHub', 'GitHub URL', 'GitHub Profile'],
      },
    ];

    for (const field of commonFields) {
      const selector = await this.findInputByLabel(page, field.labels);
      if (selector) {
        mappings.push({
          canonical_field: field.canonical,
          selector,
          type: 'input',
          label: field.labels[0],
        });
      }
    }

    // Try to find file upload for resume
    const resumeInput = await page.locator('input[type="file"]').first();
    if (await resumeInput.count() > 0) {
      mappings.push({
        canonical_field: 'resume',
        selector: 'input[type="file"]',
        type: 'input',
        label: 'Resume',
      });
    }

    return mappings;
  }

  async fill(page: Page, data: Record<string, any>): Promise<FillResult[]> {
    const results: FillResult[] = [];

    // For each data field, try to find a matching input
    for (const [canonicalField, value] of Object.entries(data)) {
      // Skip non-text fields
      if (canonicalField === 'resume' || typeof value !== 'string') {
        continue;
      }

      try {
        // Generate label variations
        const labels = this.generateLabelVariations(canonicalField);
        const selector = await this.findInputByLabel(page, labels);

        if (!selector) {
          results.push({
            field_name: canonicalField,
            value: String(value),
            success: false,
            error: 'Could not find matching field',
          });
          continue;
        }

        const element = page.locator(selector).first();
        await element.fill(String(value));
        await page.waitForTimeout(100);

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
      const fileInput = page.locator('input[type="file"]').first();
      if (await fileInput.count() > 0) {
        await fileInput.setInputFiles(filepath);
        await page.waitForTimeout(500);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Failed to attach resume:', error);
      return false;
    }
  }

  /**
   * Generate label variations for a canonical field name
   */
  private generateLabelVariations(canonicalField: string): string[] {
    const variations: Record<string, string[]> = {
      name: ['First Name', 'Name', 'Full Name', 'Your Name', 'Given Name'],
      surname: ['Last Name', 'Surname', 'Family Name'],
      email: ['Email', 'Email Address', 'E-mail', 'Your Email'],
      phone: ['Phone', 'Phone Number', 'Telephone', 'Mobile', 'Cell'],
      linkedin: ['LinkedIn', 'LinkedIn URL', 'LinkedIn Profile'],
      github: ['GitHub', 'GitHub URL', 'GitHub Profile'],
      location_city: ['City', 'Location', 'Current City'],
      location_country: ['Country', 'Location Country'],
    };

    return variations[canonicalField] || [canonicalField];
  }
}

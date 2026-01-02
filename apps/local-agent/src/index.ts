/**
 * Local Playwright Agent
 * 
 * This agent runs locally on the user's machine and handles
 * job application form prefilling using Playwright.
 * 
 * Usage:
 *   npm run dev -- <intent_id> <auth_token>
 */
import dotenv from 'dotenv';
import { ApiClient } from './utils/api-client';
import { PrefillService } from './utils/prefill-service';

dotenv.config();

const API_URL = process.env.API_URL || 'http://localhost:8000';
const SCREENSHOTS_DIR = process.env.SCREENSHOTS_DIR || './screenshots';
const HEADLESS = process.env.HEADLESS === 'true';
const STOP_BEFORE_SUBMIT = process.env.STOP_BEFORE_SUBMIT !== 'false';

async function main() {
  // Parse command line arguments
  const args = process.argv.slice(2);
  
  if (args.length < 2) {
    console.error('Usage: npm run dev -- <intent_id> <auth_token>');
    console.error('Example: npm run dev -- 507f1f77bcf86cd799439011 abc123token');
    process.exit(1);
  }

  const [intentId, authToken] = args;

  console.log('='.repeat(60));
  console.log('Jobly Local Agent - Prefill Assistant');
  console.log('='.repeat(60));
  console.log(`API URL: ${API_URL}`);
  console.log(`Intent ID: ${intentId}`);
  console.log(`Screenshots Dir: ${SCREENSHOTS_DIR}`);
  console.log(`Headless: ${HEADLESS}`);
  console.log(`Stop Before Submit: ${STOP_BEFORE_SUBMIT}`);
  console.log('='.repeat(60));

  // Initialize services
  const apiClient = new ApiClient(API_URL);
  const prefillService = new PrefillService(
    apiClient,
    SCREENSHOTS_DIR,
    STOP_BEFORE_SUBMIT
  );

  try {
    // Health check
    console.log('\nChecking API connection...');
    const isHealthy = await apiClient.healthCheck();
    if (!isHealthy) {
      console.error('ERROR: API is not responding. Please check that the backend is running.');
      process.exit(1);
    }
    console.log('✓ API connection successful');

    // Initialize browser
    console.log('\nInitializing browser...');
    await prefillService.initBrowser(HEADLESS);
    console.log('✓ Browser initialized');

    // Execute prefill
    console.log('\nExecuting prefill...');
    await prefillService.executePrefill(intentId, authToken);

    console.log('\n' + '='.repeat(60));
    console.log('SUCCESS: Prefill completed!');
    console.log('='.repeat(60));

    // Wait a bit before closing if not headless
    if (!HEADLESS) {
      console.log('\nBrowser will remain open for 10 seconds for review...');
      await new Promise(resolve => setTimeout(resolve, 10000));
    }

  } catch (error) {
    console.error('\n' + '='.repeat(60));
    console.error('ERROR: Prefill failed');
    console.error('='.repeat(60));
    console.error(error);
    process.exit(1);
  } finally {
    // Clean up
    console.log('\nClosing browser...');
    await prefillService.closeBrowser();
    console.log('✓ Browser closed');
  }
}

// Run if executed directly
if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

export { main };

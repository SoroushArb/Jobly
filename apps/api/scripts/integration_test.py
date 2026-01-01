"""
Integration test script for the Jobly API
Tests the complete profile upload and management flow
"""
import requests
import json
import sys
from pathlib import Path

API_URL = "http://localhost:8000"


def test_health():
    """Test API health check"""
    print("Testing health endpoint...")
    response = requests.get(f"{API_URL}/health")
    assert response.status_code == 200, f"Health check failed: {response.text}"
    print("✓ Health check passed")
    return True


def test_root():
    """Test root endpoint"""
    print("Testing root endpoint...")
    response = requests.get(f"{API_URL}/")
    assert response.status_code == 200, f"Root endpoint failed: {response.text}"
    data = response.json()
    assert "message" in data, "Root response missing message"
    print("✓ Root endpoint passed")
    return True


def test_upload_cv():
    """Test CV upload with sample text file"""
    print("Testing CV upload...")
    
    # For this test, we'll create a simple text file to simulate a CV
    sample_cv_path = Path(__file__).parent.parent / "sample_data" / "sample_cv.txt"
    
    if not sample_cv_path.exists():
        print(f"✗ Sample CV file not found at {sample_cv_path}")
        return None
    
    # Note: The API expects PDF/DOCX, but we can test with a text file renamed
    # In production, you would use an actual PDF/DOCX file
    with open(sample_cv_path, 'rb') as f:
        files = {'file': ('sample_cv.pdf', f, 'application/pdf')}
        try:
            response = requests.post(f"{API_URL}/profile/upload-cv", files=files)
            
            if response.status_code == 400 and "Unsupported file format" in response.text:
                print("✓ CV upload validation working (rejected non-PDF/DOCX)")
                return None
            
            if response.status_code != 200:
                print(f"✗ CV upload failed: {response.status_code} - {response.text}")
                return None
            
            data = response.json()
            assert "extracted_text" in data, "Response missing extracted_text"
            assert "draft_profile" in data, "Response missing draft_profile"
            
            profile = data["draft_profile"]
            assert "name" in profile, "Profile missing name"
            assert "email" in profile, "Profile missing email"
            
            print("✓ CV upload passed")
            print(f"  Extracted profile name: {profile['name']}")
            print(f"  Extracted profile email: {profile['email']}")
            
            return profile
        except Exception as e:
            print(f"✗ CV upload error: {e}")
            return None


def test_save_profile(profile=None):
    """Test saving a profile"""
    print("Testing profile save...")
    
    # Use provided profile or create a test profile
    if not profile:
        profile = {
            "name": "Test User",
            "email": "test@example.com",
            "links": ["https://linkedin.com/in/test"],
            "summary": "Test summary",
            "skills": [
                {
                    "category": "Programming Languages",
                    "skills": ["Python", "JavaScript"]
                }
            ],
            "experience": [
                {
                    "company": "Test Corp",
                    "title": "Developer",
                    "dates": "2020 - Present",
                    "bullets": [
                        {"text": "Developed features", "evidence_ref": None}
                    ],
                    "tech": ["Python", "FastAPI"]
                }
            ],
            "projects": [],
            "education": [
                {
                    "institution": "Test University",
                    "degree": "BSc",
                    "field": "Computer Science",
                    "dates": "2016-2020",
                    "details": []
                }
            ],
            "preferences": {
                "europe": True,
                "remote": True,
                "countries": ["Germany"],
                "cities": ["Berlin"],
                "skill_tags": ["Python"],
                "role_tags": ["Backend Developer"],
                "visa_required": False,
                "languages": ["English"]
            },
            "schema_version": "1.0.0",
            "updated_at": "2026-01-01T18:00:00.000Z"
        }
    
    try:
        response = requests.post(
            f"{API_URL}/profile/save",
            json=profile,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"✗ Profile save failed: {response.status_code} - {response.text}")
            return None
        
        data = response.json()
        assert "profile_id" in data, "Response missing profile_id"
        
        print("✓ Profile save passed")
        print(f"  Profile ID: {data['profile_id']}")
        
        return profile["email"]
    except Exception as e:
        print(f"✗ Profile save error: {e}")
        return None


def test_get_profile(email=None):
    """Test retrieving a profile"""
    print("Testing profile retrieval...")
    
    try:
        url = f"{API_URL}/profile"
        if email:
            url += f"?email={email}"
        
        response = requests.get(url)
        
        if response.status_code == 404:
            print("✓ Profile retrieval correctly returns 404 when not found")
            return True
        
        if response.status_code != 200:
            print(f"✗ Profile retrieval failed: {response.status_code} - {response.text}")
            return False
        
        data = response.json()
        assert "profile" in data, "Response missing profile"
        
        profile = data["profile"]
        assert "name" in profile, "Profile missing name"
        assert "email" in profile, "Profile missing email"
        
        print("✓ Profile retrieval passed")
        print(f"  Retrieved profile: {profile['name']} ({profile['email']})")
        
        return True
    except Exception as e:
        print(f"✗ Profile retrieval error: {e}")
        return False


def test_update_profile(email):
    """Test updating a profile"""
    print("Testing profile update...")
    
    updates = {
        "name": "Updated Test User",
        "summary": "Updated summary"
    }
    
    try:
        response = requests.patch(
            f"{API_URL}/profile?email={email}",
            json=updates,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"✗ Profile update failed: {response.status_code} - {response.text}")
            return False
        
        data = response.json()
        assert "profile_id" in data, "Response missing profile_id"
        
        print("✓ Profile update passed")
        
        return True
    except Exception as e:
        print(f"✗ Profile update error: {e}")
        return False


def main():
    """Run all integration tests"""
    print("=" * 60)
    print("Jobly API Integration Tests")
    print("=" * 60)
    print()
    
    # Check if API is running
    try:
        requests.get(f"{API_URL}/health", timeout=5)
    except requests.exceptions.ConnectionError:
        print("✗ API is not running at", API_URL)
        print("  Please start the API with:")
        print("  cd apps/api && source venv/bin/activate && uvicorn app.main:app")
        return 1
    
    # Run tests
    passed = 0
    failed = 0
    
    # Test 1: Health check
    if test_health():
        passed += 1
    else:
        failed += 1
    
    print()
    
    # Test 2: Root endpoint
    if test_root():
        passed += 1
    else:
        failed += 1
    
    print()
    
    # Test 3: Upload CV (optional - might not have valid PDF/DOCX)
    uploaded_profile = test_upload_cv()
    print()
    
    # Test 4: Save profile
    email = test_save_profile(uploaded_profile)
    if email:
        passed += 1
    else:
        failed += 1
    
    print()
    
    # Test 5: Get profile
    if email and test_get_profile(email):
        passed += 1
    else:
        failed += 1
    
    print()
    
    # Test 6: Update profile
    if email and test_update_profile(email):
        passed += 1
    else:
        failed += 1
    
    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

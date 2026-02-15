"""
Iteration 7 Testing: Login fix, QR Menu color update, Social Media TikTok/LinkedIn + Image Upload
Tests the following:
- Login with admin/admin123 credentials
- QR Menu public page - new lighter green colors (#7A8B6F)
- Social Media Publisher - all 6 platforms (Instagram, Facebook, X, TikTok, LinkedIn, WhatsApp)
- Social Media Publisher - image upload functionality
- Social Media Publisher - CRUD operations
"""
import pytest
import requests
import os
import tempfile
from PIL import Image
import io

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestLoginFix:
    """Test login with updated credentials admin/admin123"""

    def test_login_admin_admin123(self):
        """Login with admin/admin123 should work"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in response"
        assert "user" in data, "No user in response"
        assert data["user"]["username"] == "admin"
        print(f"Login successful: user={data['user']['username']}, role={data['user']['role']}")

    def test_login_wrong_password_fails(self):
        """Login with wrong password should fail"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "admin", "password": "wrongpassword"}
        )
        assert response.status_code in [401, 400], f"Expected auth failure, got {response.status_code}"


class TestQRMenuPublicPage:
    """Test QR Menu public page - lighter green colors"""

    def test_public_menu_accessible(self):
        """Public menu should be accessible without auth"""
        response = requests.get(f"{BASE_URL}/api/public/menu")
        assert response.status_code == 200
        data = response.json()
        assert "theme" in data
        assert "menu" in data
        print(f"Public menu accessible: {len(data['menu'])} categories")

    def test_public_menu_theme_lighter_green(self):
        """Theme should have lighter green colors (#7A8B6F)"""
        response = requests.get(f"{BASE_URL}/api/public/menu")
        assert response.status_code == 200
        data = response.json()
        theme = data["theme"]
        
        # Check for lighter green color scheme
        colors = theme.get("colors", {})
        bg_color = colors.get("bg", "")
        assert bg_color == "#7A8B6F", f"Expected bg color #7A8B6F, got {bg_color}"
        
        # Check gradient uses lighter green
        background = theme.get("background", {})
        gradient = background.get("value", "")
        assert "#7A8B6F" in gradient or "#6B7D60" in gradient or "#8FA385" in gradient, f"Gradient should use lighter green colors"
        print(f"Theme colors verified: bg={bg_color}")

    def test_public_theme_endpoint(self):
        """Public theme endpoint should return theme settings"""
        response = requests.get(f"{BASE_URL}/api/public/theme")
        assert response.status_code == 200
        data = response.json()
        assert "colors" in data
        assert data["colors"]["bg"] == "#7A8B6F"


class TestSocialMediaPlatforms:
    """Test Social Media - all 6 platforms visible"""

    def test_social_templates_six_platforms(self):
        """Templates endpoint should return frame styles"""
        response = requests.get(f"{BASE_URL}/api/social/templates")
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert "frame_styles" in data
        assert len(data["frame_styles"]) == 5, f"Expected 5 frame styles, got {len(data['frame_styles'])}"

    def test_create_post_with_all_platforms(self):
        """Create post with all 6 platforms"""
        platforms = ["instagram", "facebook", "twitter", "tiktok", "linkedin", "whatsapp"]
        post_data = {
            "title": "TEST_All Platforms Test",
            "content": "Testing all 6 platforms: Instagram, Facebook, X, TikTok, LinkedIn, WhatsApp",
            "platforms": platforms,
            "post_type": "text",
            "hashtags": ["Test", "AllPlatforms"],
            "status": "draft"
        }
        
        response = requests.post(f"{BASE_URL}/api/social/posts", json=post_data)
        assert response.status_code == 200, f"Create post failed: {response.text}"
        data = response.json()
        
        assert data["platforms"] == platforms, f"Expected all 6 platforms, got {data['platforms']}"
        assert "id" in data
        
        # Cleanup
        post_id = data["id"]
        delete_response = requests.delete(f"{BASE_URL}/api/social/posts/{post_id}")
        assert delete_response.status_code == 200
        print(f"Created and deleted post with all 6 platforms")


class TestSocialMediaImageUpload:
    """Test Social Media - image upload functionality"""

    def test_upload_image_jpeg(self):
        """Upload JPEG image should work"""
        # Create a test image
        img = Image.new('RGB', (100, 100), color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        files = {'file': ('test.jpg', img_bytes, 'image/jpeg')}
        response = requests.post(f"{BASE_URL}/api/social/upload-image", files=files)
        assert response.status_code == 200, f"Upload failed: {response.text}"
        data = response.json()
        assert data["success"] == True
        assert "image_url" in data
        assert data["image_url"].startswith("/uploads/social/")
        print(f"Uploaded image: {data['image_url']}")

    def test_upload_image_png(self):
        """Upload PNG image should work"""
        img = Image.new('RGBA', (100, 100), color='green')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        files = {'file': ('test.png', img_bytes, 'image/png')}
        response = requests.post(f"{BASE_URL}/api/social/upload-image", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "image_url" in data

    def test_upload_image_webp(self):
        """Upload WEBP image should work"""
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='WEBP')
        img_bytes.seek(0)
        
        files = {'file': ('test.webp', img_bytes, 'image/webp')}
        response = requests.post(f"{BASE_URL}/api/social/upload-image", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True

    def test_upload_invalid_file_type_rejected(self):
        """Upload non-image file should be rejected"""
        files = {'file': ('test.txt', b'This is not an image', 'text/plain')}
        response = requests.post(f"{BASE_URL}/api/social/upload-image", files=files)
        assert response.status_code == 400, f"Expected 400 for invalid file type, got {response.status_code}"

    def test_create_post_with_image(self):
        """Create a post with an uploaded image"""
        # First upload an image
        img = Image.new('RGB', (100, 100), color='purple')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        files = {'file': ('test.jpg', img_bytes, 'image/jpeg')}
        upload_response = requests.post(f"{BASE_URL}/api/social/upload-image", files=files)
        assert upload_response.status_code == 200
        image_url = upload_response.json()["image_url"]
        
        # Create post with image
        post_data = {
            "title": "TEST_Post with Image",
            "content": "This post has an image attached",
            "platforms": ["instagram"],
            "post_type": "text",
            "hashtags": ["TestImage"],
            "status": "draft",
            "image_url": image_url
        }
        
        response = requests.post(f"{BASE_URL}/api/social/posts", json=post_data)
        assert response.status_code == 200
        data = response.json()
        assert data["image_url"] == image_url, f"Image URL not saved correctly"
        
        # Verify by getting the post
        get_response = requests.get(f"{BASE_URL}/api/social/posts/{data['id']}")
        assert get_response.status_code == 200
        assert get_response.json()["image_url"] == image_url
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/social/posts/{data['id']}")
        print(f"Created post with image: {image_url}")


class TestSocialMediaCRUD:
    """Test Social Media CRUD operations"""

    def test_create_update_delete_post(self):
        """Full CRUD cycle for social media post"""
        # CREATE
        post_data = {
            "title": "TEST_CRUD Post",
            "content": "Testing CRUD operations",
            "platforms": ["facebook", "tiktok"],
            "post_type": "promo",
            "hashtags": ["Test", "CRUD"],
            "status": "draft"
        }
        
        create_response = requests.post(f"{BASE_URL}/api/social/posts", json=post_data)
        assert create_response.status_code == 200
        created = create_response.json()
        post_id = created["id"]
        assert created["title"] == "TEST_CRUD Post"
        
        # READ
        get_response = requests.get(f"{BASE_URL}/api/social/posts/{post_id}")
        assert get_response.status_code == 200
        fetched = get_response.json()
        assert fetched["title"] == "TEST_CRUD Post"
        
        # UPDATE
        update_data = {"title": "TEST_Updated CRUD Post", "platforms": ["instagram", "linkedin", "whatsapp"]}
        update_response = requests.patch(f"{BASE_URL}/api/social/posts/{post_id}", json=update_data)
        assert update_response.status_code == 200
        updated = update_response.json()
        assert updated["title"] == "TEST_Updated CRUD Post"
        assert set(updated["platforms"]) == {"instagram", "linkedin", "whatsapp"}
        
        # Verify update persisted
        verify_response = requests.get(f"{BASE_URL}/api/social/posts/{post_id}")
        assert verify_response.json()["title"] == "TEST_Updated CRUD Post"
        
        # DELETE
        delete_response = requests.delete(f"{BASE_URL}/api/social/posts/{post_id}")
        assert delete_response.status_code == 200
        
        # Verify deletion
        verify_deleted = requests.get(f"{BASE_URL}/api/social/posts/{post_id}")
        assert verify_deleted.status_code == 404
        print("CRUD cycle completed successfully")

    def test_publish_post_mocked(self):
        """Test publish post (MOCKED - marks as published in DB)"""
        # Create draft post
        post_data = {
            "title": "TEST_Publish Test",
            "content": "Testing publish feature",
            "platforms": ["instagram"],
            "status": "draft"
        }
        create_response = requests.post(f"{BASE_URL}/api/social/posts", json=post_data)
        post_id = create_response.json()["id"]
        
        # Publish
        publish_response = requests.post(f"{BASE_URL}/api/social/posts/{post_id}/publish")
        assert publish_response.status_code == 200
        assert "success" in publish_response.json()
        
        # Verify status changed
        get_response = requests.get(f"{BASE_URL}/api/social/posts/{post_id}")
        assert get_response.json()["status"] == "published"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/social/posts/{post_id}")
        print("Publish (MOCKED) test completed")

    def test_social_stats(self):
        """Test stats endpoint"""
        response = requests.get(f"{BASE_URL}/api/social/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "published" in data
        assert "drafts" in data
        assert "scheduled" in data
        print(f"Stats: total={data['total']}, published={data['published']}, drafts={data['drafts']}")


class TestHealthAndSetup:
    """Basic health and setup tests"""

    def test_health_endpoint(self):
        """Health endpoint should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

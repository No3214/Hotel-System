"""
Iteration 6 Tests - QR Menu Update (100 items, 16 categories) + Social Media Publisher
Tests for:
1. Public Menu API - 16 categories, 100+ items
2. Social Media CRUD - posts, templates, stats, publish
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# ==================== PUBLIC MENU TESTS ====================
class TestPublicMenu:
    """Test updated QR Menu with 100 items and 16 categories"""

    def test_public_menu_returns_16_categories(self):
        """Verify menu has exactly 16 categories as per requirements"""
        response = requests.get(f"{BASE_URL}/api/public/menu")
        assert response.status_code == 200
        
        data = response.json()
        assert "menu" in data
        categories = list(data["menu"].keys())
        
        # Verify 16 categories
        assert len(categories) == 16, f"Expected 16 categories, got {len(categories)}"
        
        # Verify expected category keys
        expected_categories = [
            "kahvalti", "ekstralar", "baslangic", "pizza_sandvic", "peynir",
            "ana_yemek", "ara_sicak", "meze", "tatli", "sicak_icecekler",
            "soguk_icecekler", "sarap", "kokteyl", "bira", "viski", "raki"
        ]
        for cat in expected_categories:
            assert cat in categories, f"Missing category: {cat}"
        print(f"✓ Found all 16 categories: {categories}")

    def test_public_menu_has_100_plus_items(self):
        """Verify menu has 100+ items total"""
        response = requests.get(f"{BASE_URL}/api/public/menu")
        assert response.status_code == 200
        
        data = response.json()
        total_items = 0
        for cat_key, cat_data in data["menu"].items():
            total_items += len(cat_data.get("items", []))
        
        assert total_items >= 100, f"Expected 100+ items, got {total_items}"
        print(f"✓ Total menu items: {total_items}")

    def test_public_menu_theme_has_white_logo(self):
        """Verify theme uses white logo (KOZBEYLI_BEYAZ_LOGO.png)"""
        response = requests.get(f"{BASE_URL}/api/public/menu")
        assert response.status_code == 200
        
        data = response.json()
        assert "theme" in data
        theme = data["theme"]
        
        # Check logo_url
        assert "logo_url" in theme
        assert "KOZBEYLI_BEYAZ_LOGO.png" in theme["logo_url"], f"Expected white logo, got: {theme['logo_url']}"
        print(f"✓ White logo configured: {theme['logo_url']}")

    def test_public_menu_theme_colors(self):
        """Verify theme has olive green colors"""
        response = requests.get(f"{BASE_URL}/api/public/menu")
        assert response.status_code == 200
        
        theme = response.json()["theme"]
        colors = theme.get("colors", {})
        
        # Check olive green background
        assert colors.get("bg") == "#515249", f"Expected olive bg #515249, got: {colors.get('bg')}"
        assert colors.get("text") == "#F8F5EF", f"Expected cream text, got: {colors.get('text')}"
        print(f"✓ Theme colors verified: bg={colors.get('bg')}, text={colors.get('text')}")

    def test_public_menu_uses_alifira_font(self):
        """Verify theme uses Alifira font for headings"""
        response = requests.get(f"{BASE_URL}/api/public/menu")
        assert response.status_code == 200
        
        theme = response.json()["theme"]
        assert theme.get("font_heading") == "Alifira", f"Expected Alifira font, got: {theme.get('font_heading')}"
        print(f"✓ Alifira font configured")

    def test_public_menu_category_structure(self):
        """Verify each category has required fields"""
        response = requests.get(f"{BASE_URL}/api/public/menu")
        assert response.status_code == 200
        
        menu = response.json()["menu"]
        for cat_key, cat_data in menu.items():
            assert "name_tr" in cat_data, f"Missing name_tr in {cat_key}"
            assert "name_en" in cat_data, f"Missing name_en in {cat_key}"
            assert "icon" in cat_data, f"Missing icon in {cat_key}"
            assert "items" in cat_data, f"Missing items in {cat_key}"
            
            # Verify items structure
            for item in cat_data["items"]:
                assert "name" in item, f"Missing name in item"
                assert "price_try" in item, f"Missing price_try in item"
        print(f"✓ All category structures valid")


# ==================== SOCIAL MEDIA TESTS ====================
class TestSocialMediaPosts:
    """Test Social Media CRUD operations"""

    def test_get_posts_empty_list(self):
        """Get posts - should return posts array"""
        response = requests.get(f"{BASE_URL}/api/social/posts")
        assert response.status_code == 200
        
        data = response.json()
        assert "posts" in data
        assert isinstance(data["posts"], list)
        print(f"✓ GET /social/posts returns {len(data['posts'])} posts")

    def test_create_post(self):
        """Create a new social media post"""
        post_data = {
            "title": "TEST_Post_Iteration6",
            "content": "Bu bir test goenderisidir.",
            "platforms": ["instagram", "facebook"],
            "post_type": "text",
            "frame_style": "default",
            "hashtags": ["KozbeyliKonagi", "Test"],
            "status": "draft"
        }
        
        response = requests.post(f"{BASE_URL}/api/social/posts", json=post_data)
        assert response.status_code == 200, f"Create failed: {response.text}"
        
        data = response.json()
        assert "id" in data
        assert data["title"] == post_data["title"]
        assert data["content"] == post_data["content"]
        assert data["platforms"] == post_data["platforms"]
        assert data["status"] == "draft"
        
        # Store for cleanup
        TestSocialMediaPosts.created_post_id = data["id"]
        print(f"✓ Created post: {data['id']}")
        return data["id"]

    def test_get_single_post(self):
        """Get a single post by ID"""
        # First create a post
        post_data = {"title": "TEST_SinglePost", "content": "Test content", "platforms": [], "post_type": "text"}
        create_resp = requests.post(f"{BASE_URL}/api/social/posts", json=post_data)
        post_id = create_resp.json()["id"]
        
        # Get the post
        response = requests.get(f"{BASE_URL}/api/social/posts/{post_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == post_id
        assert data["title"] == "TEST_SinglePost"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/social/posts/{post_id}")
        print(f"✓ GET single post works")

    def test_update_post(self):
        """Update an existing post"""
        # Create
        post_data = {"title": "TEST_UpdatePost", "content": "Original", "platforms": [], "post_type": "text"}
        create_resp = requests.post(f"{BASE_URL}/api/social/posts", json=post_data)
        post_id = create_resp.json()["id"]
        
        # Update
        update_data = {"title": "TEST_UpdatePost_Modified", "content": "Updated content"}
        response = requests.patch(f"{BASE_URL}/api/social/posts/{post_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "TEST_UpdatePost_Modified"
        assert data["content"] == "Updated content"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/social/posts/{post_id}")
        print(f"✓ PATCH post works")

    def test_delete_post(self):
        """Delete a post"""
        # Create
        post_data = {"title": "TEST_DeletePost", "content": "To be deleted", "platforms": [], "post_type": "text"}
        create_resp = requests.post(f"{BASE_URL}/api/social/posts", json=post_data)
        post_id = create_resp.json()["id"]
        
        # Delete
        response = requests.delete(f"{BASE_URL}/api/social/posts/{post_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        
        # Verify deleted
        get_resp = requests.get(f"{BASE_URL}/api/social/posts/{post_id}")
        assert get_resp.status_code == 404
        print(f"✓ DELETE post works")

    def test_publish_post(self):
        """Publish a post (marks as published - MOCKED)"""
        # Create draft
        post_data = {"title": "TEST_PublishPost", "content": "To be published", "platforms": ["instagram"], "post_type": "promo", "status": "draft"}
        create_resp = requests.post(f"{BASE_URL}/api/social/posts", json=post_data)
        post_id = create_resp.json()["id"]
        
        # Publish
        response = requests.post(f"{BASE_URL}/api/social/posts/{post_id}/publish")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        
        # Verify status changed
        get_resp = requests.get(f"{BASE_URL}/api/social/posts/{post_id}")
        assert get_resp.json()["status"] == "published"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/social/posts/{post_id}")
        print(f"✓ POST publish works (MOCKED - marks as published)")


class TestSocialMediaTemplatesAndStats:
    """Test templates and stats endpoints"""

    def test_get_templates(self):
        """Get post templates and frame styles"""
        response = requests.get(f"{BASE_URL}/api/social/templates")
        assert response.status_code == 200
        
        data = response.json()
        assert "templates" in data
        assert "frame_styles" in data
        
        # Verify 5 template types
        templates = data["templates"]
        expected_types = ["text", "promo", "event", "menu_highlight", "announcement"]
        for t in expected_types:
            assert t in templates, f"Missing template type: {t}"
        
        # Verify 5 frame styles
        frame_styles = data["frame_styles"]
        assert len(frame_styles) == 5
        expected_styles = ["default", "elegant", "bold", "minimal", "festive"]
        style_ids = [s["id"] for s in frame_styles]
        for s in expected_styles:
            assert s in style_ids, f"Missing frame style: {s}"
        
        print(f"✓ Templates: {list(templates.keys())}")
        print(f"✓ Frame styles: {style_ids}")

    def test_get_stats(self):
        """Get social media stats"""
        response = requests.get(f"{BASE_URL}/api/social/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total" in data
        assert "published" in data
        assert "drafts" in data
        assert "scheduled" in data
        assert "platforms" in data
        
        print(f"✓ Stats: total={data['total']}, published={data['published']}, drafts={data['drafts']}")

    def test_filter_posts_by_status(self):
        """Test filtering posts by status"""
        # Create posts with different statuses
        draft = {"title": "TEST_DraftFilter", "content": "Draft", "platforms": [], "post_type": "text", "status": "draft"}
        scheduled = {"title": "TEST_ScheduledFilter", "content": "Scheduled", "platforms": [], "post_type": "text", "status": "scheduled"}
        
        d_resp = requests.post(f"{BASE_URL}/api/social/posts", json=draft)
        s_resp = requests.post(f"{BASE_URL}/api/social/posts", json=scheduled)
        d_id = d_resp.json()["id"]
        s_id = s_resp.json()["id"]
        
        # Filter drafts
        resp_draft = requests.get(f"{BASE_URL}/api/social/posts?status=draft")
        draft_posts = resp_draft.json()["posts"]
        assert any(p["id"] == d_id for p in draft_posts)
        
        # Filter scheduled
        resp_sched = requests.get(f"{BASE_URL}/api/social/posts?status=scheduled")
        sched_posts = resp_sched.json()["posts"]
        assert any(p["id"] == s_id for p in sched_posts)
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/social/posts/{d_id}")
        requests.delete(f"{BASE_URL}/api/social/posts/{s_id}")
        print(f"✓ Status filtering works")


# ==================== CLEANUP ====================
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_posts():
    """Cleanup TEST_ prefixed posts after all tests"""
    yield
    # Cleanup
    resp = requests.get(f"{BASE_URL}/api/social/posts")
    if resp.status_code == 200:
        for post in resp.json().get("posts", []):
            if post.get("title", "").startswith("TEST_"):
                requests.delete(f"{BASE_URL}/api/social/posts/{post['id']}")

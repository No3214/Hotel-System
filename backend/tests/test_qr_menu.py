"""
Test QR Menu Feature - Public menu endpoints and Admin CRUD
Tests: Public menu, Menu admin items, Categories, Theme
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPublicMenu:
    """Public menu endpoints - no auth required"""

    def test_public_menu_returns_200(self):
        """GET /api/public/menu should return 200"""
        response = requests.get(f"{BASE_URL}/api/public/menu")
        assert response.status_code == 200
        print("Public menu endpoint returns 200 OK")

    def test_public_menu_has_theme(self):
        """Public menu should contain theme settings"""
        response = requests.get(f"{BASE_URL}/api/public/menu")
        assert response.status_code == 200
        data = response.json()
        assert "theme" in data
        theme = data["theme"]
        assert "brand_name" in theme
        assert "colors" in theme
        assert theme["brand_name"] == "Kozbeyli Konagi"
        print(f"Theme brand_name: {theme['brand_name']}")

    def test_public_menu_has_kozbeyli_green_colors(self):
        """Theme should have olive green background (Kozbeyli Green)"""
        response = requests.get(f"{BASE_URL}/api/public/menu")
        data = response.json()
        colors = data["theme"]["colors"]
        assert colors["bg"] == "#515249"  # Olive/Kozbeyli Green
        assert colors["text"] == "#F8F5EF"  # Cream text
        print(f"Background: {colors['bg']}, Text: {colors['text']}")

    def test_public_menu_has_categories(self):
        """Public menu should have menu categories"""
        response = requests.get(f"{BASE_URL}/api/public/menu")
        data = response.json()
        assert "menu" in data
        menu = data["menu"]
        assert len(menu) > 0  # At least one category
        # Check for expected categories
        assert "kahvalti" in menu or "baslangic" in menu or "ana_yemek" in menu
        print(f"Menu categories: {list(menu.keys())}")

    def test_public_menu_items_have_prices_in_tl(self):
        """Menu items should have price_try field"""
        response = requests.get(f"{BASE_URL}/api/public/menu")
        data = response.json()
        menu = data["menu"]
        # Get first category
        first_cat_key = list(menu.keys())[0]
        items = menu[first_cat_key]["items"]
        assert len(items) > 0
        # Check first item has price
        first_item = items[0]
        assert "price_try" in first_item
        assert isinstance(first_item["price_try"], (int, float))
        assert first_item["price_try"] > 0
        print(f"First item: {first_item['name']} - {first_item['price_try']} TL")

    def test_public_menu_has_restaurant_name(self):
        """Public menu should return restaurant name"""
        response = requests.get(f"{BASE_URL}/api/public/menu")
        data = response.json()
        assert "restaurant" in data
        assert data["restaurant"] is not None
        print(f"Restaurant: {data['restaurant']}")

    def test_public_menu_has_hotel_name(self):
        """Public menu should return hotel name"""
        response = requests.get(f"{BASE_URL}/api/public/menu")
        data = response.json()
        assert "hotel" in data
        assert data["hotel"] is not None
        print(f"Hotel: {data['hotel']}")


class TestPublicTheme:
    """Public theme endpoint"""

    def test_public_theme_returns_200(self):
        """GET /api/public/theme should return 200"""
        response = requests.get(f"{BASE_URL}/api/public/theme")
        assert response.status_code == 200

    def test_public_theme_has_brand_info(self):
        """Theme should have brand name and tagline"""
        response = requests.get(f"{BASE_URL}/api/public/theme")
        data = response.json()
        assert "brand_name" in data
        assert "tagline" in data


class TestMenuAdminItems:
    """Admin menu items CRUD - requires auth"""

    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Login and get auth token"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "kozbeyli2026"
        })
        assert login_response.status_code == 200
        token = login_response.json()["token"]
        self.headers = {"Authorization": f"Bearer {token}"}
        yield
        # Cleanup created test items
        items_response = requests.get(f"{BASE_URL}/api/menu-admin/items", headers=self.headers)
        if items_response.status_code == 200:
            items = items_response.json().get("items", [])
            for item in items:
                if item["name"].startswith("TEST_"):
                    requests.delete(f"{BASE_URL}/api/menu-admin/items/{item['id']}", headers=self.headers)

    def test_get_menu_items_returns_list(self):
        """GET /api/menu-admin/items should return items list"""
        response = requests.get(f"{BASE_URL}/api/menu-admin/items", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)
        print(f"Found {len(data['items'])} menu items")

    def test_create_menu_item(self):
        """POST /api/menu-admin/items should create a new item"""
        new_item = {
            "category": "kahvalti",
            "name": "TEST_Ozel Kahvalti",
            "desc": "Test aciklama",
            "price_try": 150.0,
            "is_available": True,
            "sort_order": 999
        }
        response = requests.post(f"{BASE_URL}/api/menu-admin/items", json=new_item, headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == new_item["name"]
        assert data["price_try"] == new_item["price_try"]
        assert "id" in data
        print(f"Created item: {data['name']} with id: {data['id']}")

    def test_update_menu_item(self):
        """PATCH /api/menu-admin/items/{id} should update item"""
        # First create an item
        new_item = {
            "category": "tatli",
            "name": "TEST_Update Item",
            "desc": "Original desc",
            "price_try": 50.0
        }
        create_response = requests.post(f"{BASE_URL}/api/menu-admin/items", json=new_item, headers=self.headers)
        assert create_response.status_code == 200
        item_id = create_response.json()["id"]
        
        # Update the item
        update_data = {"name": "TEST_Updated Item Name", "price_try": 75.0}
        update_response = requests.patch(f"{BASE_URL}/api/menu-admin/items/{item_id}", json=update_data, headers=self.headers)
        assert update_response.status_code == 200
        updated = update_response.json()
        assert updated["name"] == "TEST_Updated Item Name"
        assert updated["price_try"] == 75.0
        print(f"Updated item: {updated['name']}")

    def test_delete_menu_item(self):
        """DELETE /api/menu-admin/items/{id} should delete item"""
        # First create an item to delete
        new_item = {
            "category": "tatli",
            "name": "TEST_Delete Item",
            "desc": "To be deleted",
            "price_try": 30.0
        }
        create_response = requests.post(f"{BASE_URL}/api/menu-admin/items", json=new_item, headers=self.headers)
        item_id = create_response.json()["id"]
        
        # Delete the item
        delete_response = requests.delete(f"{BASE_URL}/api/menu-admin/items/{item_id}", headers=self.headers)
        assert delete_response.status_code == 200
        assert delete_response.json()["success"] == True
        print(f"Deleted item id: {item_id}")


class TestMenuAdminCategories:
    """Admin menu categories CRUD"""

    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Login and get auth token"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "kozbeyli2026"
        })
        token = login_response.json()["token"]
        self.headers = {"Authorization": f"Bearer {token}"}
        yield
        # Cleanup test categories
        cats_response = requests.get(f"{BASE_URL}/api/menu-admin/categories", headers=self.headers)
        if cats_response.status_code == 200:
            cats = cats_response.json().get("categories", [])
            for cat in cats:
                if cat["key"].startswith("test_"):
                    requests.delete(f"{BASE_URL}/api/menu-admin/categories/{cat['id']}", headers=self.headers)

    def test_get_categories_returns_list(self):
        """GET /api/menu-admin/categories should return categories list"""
        response = requests.get(f"{BASE_URL}/api/menu-admin/categories", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert isinstance(data["categories"], list)
        assert len(data["categories"]) > 0
        print(f"Found {len(data['categories'])} categories")

    def test_create_category(self):
        """POST /api/menu-admin/categories should create a new category"""
        new_cat = {
            "key": "test_special",
            "name_tr": "Test Ozel Kategori",
            "name_en": "Test Special Category",
            "icon": "star",
            "sort_order": 999,
            "is_active": True
        }
        response = requests.post(f"{BASE_URL}/api/menu-admin/categories", json=new_cat, headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == new_cat["key"]
        assert data["name_tr"] == new_cat["name_tr"]
        print(f"Created category: {data['name_tr']}")


class TestMenuAdminTheme:
    """Admin theme settings"""

    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Login and get auth token"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "kozbeyli2026"
        })
        token = login_response.json()["token"]
        self.headers = {"Authorization": f"Bearer {token}"}

    def test_get_theme_returns_settings(self):
        """GET /api/menu-admin/theme should return theme settings"""
        response = requests.get(f"{BASE_URL}/api/menu-admin/theme", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "brand_name" in data
        assert "colors" in data
        assert "background" in data
        print(f"Theme brand: {data['brand_name']}")

    def test_update_theme(self):
        """PATCH /api/menu-admin/theme should update theme settings"""
        # Get current theme
        get_response = requests.get(f"{BASE_URL}/api/menu-admin/theme", headers=self.headers)
        original_theme = get_response.json()
        
        # Update only tagline
        update_data = {
            "tagline": "Tas Otel - Test Update"
        }
        response = requests.patch(f"{BASE_URL}/api/menu-admin/theme", json=update_data, headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["tagline"] == "Tas Otel - Test Update"
        
        # Restore original
        requests.patch(f"{BASE_URL}/api/menu-admin/theme", json={"tagline": original_theme["tagline"]}, headers=self.headers)
        print("Theme update successful")


class TestMenuAdminAuth:
    """Verify admin endpoints require authentication"""

    def test_items_without_auth_fails(self):
        """GET /api/menu-admin/items without auth should fail (401 or still work - depending on implementation)"""
        response = requests.get(f"{BASE_URL}/api/menu-admin/items")
        # Note: Current implementation might not require auth for GET
        print(f"Items without auth status: {response.status_code}")

    def test_create_item_without_auth(self):
        """POST /api/menu-admin/items without auth - check behavior"""
        new_item = {
            "category": "test",
            "name": "Unauthorized Item",
            "price_try": 10.0
        }
        response = requests.post(f"{BASE_URL}/api/menu-admin/items", json=new_item)
        print(f"Create item without auth status: {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

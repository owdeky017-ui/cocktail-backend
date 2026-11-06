def make_cocktail(client):
    gin = client.post("/ingredients", json={"name": "Gin", "kind": "base"}).json()
    lime = client.post("/ingredients", json={"name": "Lime Juice", "kind": "juice"}).json()
    payload = {
        "name": "Gimlet",
        "instructions": "Shake with ice and strain into a chilled glass.",
        "glass": "Coupe",
        "category": "Sour",
        "image_url": "https://example.com/gimlet.jpg",
        "items": [
            {"ingredient_id": gin["id"], "quantity": 2, "unit": "oz"},
            {"ingredient_id": lime["id"], "quantity": 0.75, "unit": "oz"}
        ]
    }
    return client.post("/cocktails", json=payload).json()


def test_health_return_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_ingredient(client):
    client.post("/ingredients", json={"name": "Gin", "kind": "base"})
    response = client.post("/ingredients", json={"name": "Gin", "kind": "base"})
    assert response.status_code == 400


def test_list_ingredients_by_kind(client):
    client.post("/ingredients", json={"name": "Gin", "kind": "base"})
    client.post("/ingredients", json={"name": "Lime Juice", "kind": "juice"})
    response = client.get("/ingredients", params={"kind": "juice"})
    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == [ "Lime Juice"]


def test_create_cocktail_return_nested_items(client):
    cocktail = make_cocktail(client)
    assert cocktail["name"] == "Gimlet"
    assert len(cocktail["items"]) == 2
    assert cocktail["items"][0]["ingredient"]["name"] == "Gin"


def test_create_cocktail_with_unknown_ingredient_returns_400(client):
    payload = {
        "name": "Ghost",
        "instructions": "Just mix it.",
        "glass": "Any",
        "category": "Unknown",
        "image_url": "",
        "items": [
            {"ingredient_id": 999, "quantity": 1, "unit": "oz"}
        ]
    }
    response = client.post("/cocktails", json=payload)
    assert response.status_code == 400


def test_get_cocktail_returns_404_for_nonexistent(client):
    response = client.get("/cocktails/999")
    assert response.status_code == 404


def test_update_cocktail_replaces_insructions_and_items(client):
    cocktail = make_cocktail(client)
    payload = {
        "name": "Gimlet",
        "instructions": "Stir with ice and strain into a chilled glass.",
        "glass": "Coupe",
        "category": "Sour",
        "image_url": "https://example.com/gimlet.jpg",
        "items": [
            {"ingredient_id": cocktail["items"][0]["ingredient"]["id"], "quantity": 1.5, "unit": "oz"},
            {"ingredient_id": cocktail["items"][1]["ingredient"]["id"], "quantity": 0.5, "unit": "oz"}
        ]
    }
    response = client.put(f"/cocktails/{cocktail['id']}", json=payload)
    assert response.status_code == 200
    updated_cocktail = response.json()
    assert updated_cocktail["instructions"] == payload["instructions"]
    assert len(updated_cocktail["items"]) == 2
    assert updated_cocktail["items"][0]["quantity"] == 1.5
    assert updated_cocktail["items"][1]["quantity"] == 0.5


def test_delete_cocktail(client):
    cocktail = make_cocktail(client)
    response = client.delete(f"/cocktails/{cocktail['id']}")
    assert response.status_code == 204
    response = client.get(f"/cocktails/{cocktail['id']}")
    assert response.status_code == 404


def test_delete_ingreddient_still_in_recipe_returns_400(client):
    cocktail = make_cocktail(client)
    ingredient_id = cocktail["items"][0]["ingredient"]["id"]
    response = client.delete(f"/ingredients/{ingredient_id}")
    assert response.status_code == 400


def test_suggest_puts_full_match_first(client):
    make_cocktail(client)
    response = client.get("/suggest", params={"available_ingredients": ["Gin", "Lime Juice"]})
    assert response.status_code == 200
    suggestions = response.json()
    assert len(suggestions) == 1.0
    assert suggestions[0]["name"] == "Gimlet"


def test_scale_doubles_quantities(client):
    cocktail = make_cocktail(client)
    response = client.get(f"/cocktails/{cocktail['id']}/scale", params={"servings": 2})
    assert response.status_code == 200
    scaled_cocktail = response.json()
    assert scaled_cocktail["items"][0]["amount"] == "4 oz"
    assert scaled_cocktail["items"][1]["amount"] == "1.5 oz"


def test_scale_leaves_millilitres_empty_for_piece_units(client):
    lemon = client.post("/ingredients", json={"name": "Lemon twist", "kind": "garnish"}).json()
    payload = {
        "name": "Twist Sour",
        "instructions": "Express the twist over the glass",
        "items": [{"quantity": 1, "unit": "piece", "ingredient_id": lemon["id"]}],
        }
    cocktail = client.post("/cocktails", json=payload).json()
    response = client.get(f"/cocktails/{cocktail['id']}/scale", params={"servings": 3})
    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["amount"] == "3 piece"
    assert item["millilitres"] is None

def test_scale_returns_404_for_unknown_id(client):
    response = client.get("/cocktails/999/scale", params={"servings": 2})
    assert response.status_code == 404


def test_scale_rejects_zero_servings(client):
    cocktail = make_cocktail(client)
    response = client.get(f"/cocktails/{cocktail['id']}/scale", params={"servings": 0})
    assert response.status_code ==422
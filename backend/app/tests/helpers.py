from httpx import AsyncClient


async def create_test_user(
    client: AsyncClient,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "testpassword123",
    contact_number: str = "87770001122",
) -> dict:
    response = await client.post(
        "/api/users/auth/sign-up",
        json={
            "username": username,
            "email": email,
            "password": password,
            "contact_number": contact_number,
        },
    )
    # TODO change status_code to 201
    assert response.status_code == 200, f"Failed to create user: {response.text}"
    return response.json()


async def login_user(
    client: AsyncClient,
    email: str = "test@example.com",
    password: str = "testpassword123",
) -> str:
    response = await client.post(
        "/api/users/auth/sign-in",
        data={
            "username": email,
            "password": password,
        },
    )
    assert response.status_code == 200, f"Failed to login: {response.text}"
    return response.json()["access_token"]


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}

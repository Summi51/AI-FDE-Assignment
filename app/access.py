"""Role scope. A territory manager never sees another territory."""


class AccessDenied(Exception):
    pass


def load_user(con, user_id: str) -> dict:
    row = con.execute(
        """
        select user_id, role, region, sub_region, territory_code, primary_language
        from users_and_roles
        where user_id = ?
        """,
        [user_id],
    ).fetchone()
    if not row:
        raise AccessDenied(f"Unknown user {user_id}")
    return {
        "user_id": row[0],
        "role": row[1],
        "region": row[2],
        "sub_region": row[3],
        "territory_code": row[4],
        "language": row[5],
    }


def territory_scope(user: dict, requested: str | None) -> str:
    """Return the only territory this user may query, or raise."""
    role = user["role"]
    own = user["territory_code"]
    if role == "Territory Manager":
        if not own:
            raise AccessDenied("Territory manager has no territory assigned")
        if requested and requested != own:
            raise AccessDenied(
                f"{user['user_id']} can only see {own}, not {requested}"
            )
        return own
    if role in {"Global Sales Head", "Global Finance Controller", "BI Analyst"}:
        if not requested:
            raise AccessDenied("Global roles must name a territory for a visit brief")
        return requested
    if role == "Regional Sales Manager":
        if not requested:
            raise AccessDenied("Name a territory in your sub-region")
        return requested
    raise AccessDenied(f"Role {role} cannot open a distributor visit brief")


def assert_distributor_in_scope(con, user: dict, distributor_id: str) -> dict:
    territory = territory_scope(user, None) if user["role"] == "Territory Manager" else None
    row = con.execute(
        """
        select distributor_id, distributor_name, territory_code, region_code,
               currency, credit_limit_local, tier
        from distributors
        where distributor_id = ?
        """,
        [distributor_id],
    ).fetchone()
    if not row:
        raise AccessDenied(f"Unknown distributor {distributor_id}")
    dist = {
        "distributor_id": row[0],
        "name": row[1],
        "territory_code": row[2],
        "region_code": row[3],
        "currency": row[4],
        "credit_limit": row[5],
        "tier": row[6],
    }
    allowed = territory_scope(user, dist["territory_code"])
    if dist["territory_code"] != allowed:
        raise AccessDenied("Distributor is outside your scope")
    if user["role"] == "Regional Sales Manager":
        sub = con.execute(
            "select sub_region from territories where territory_code = ?",
            [dist["territory_code"]],
        ).fetchone()
        if not sub or sub[0] != user["sub_region"]:
            raise AccessDenied("Territory is outside your sub-region")
    return dist

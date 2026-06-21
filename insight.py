def get_insight(pop: int) -> dict:
    if pop >= 60:
        return {
            "color": "red",
            "message": "내일은 비 예보로 인해 유동인구가 평소 대비 감소할 확률이 높습니다. 재료 발주량을 평소보다 줄이시는 것을 추천합니다.",
        }
    elif pop >= 30:
        return {
            "color": "orange",
            "message": "비 가능성이 있습니다. 재료를 평소의 90% 수준으로 준비하고 당일 상황을 지켜보세요.",
        }
    else:
        return {
            "color": "green",
            "message": "내일은 맑은 날씨로 유동인구가 평소 수준이 될 것으로 예상됩니다. 평소대로 운영하세요.",
        }

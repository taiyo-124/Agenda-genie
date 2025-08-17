def greet(name: str) -> str:
    """
    指定された名前で挨拶文を作成します。

    Args:
        name: 挨拶する相手の名前。

    Returns:
        挨拶文の文字列。
    """
    return f"Hello, {name}!"


if __name__ == "__main__":
    message = greet("Agenda Genie")
    print(message)

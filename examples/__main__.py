if __name__ == "__main__":
    if __package__:
        from .say_hello import main
    else:
        from say_hello import main

    raise SystemExit(main())

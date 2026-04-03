def order_rename_graph(input_graph: "list[tuple[str, str]]") -> "list[tuple[str, str]]":
    """Topologically sorts the given input graph, as represented by its vertices

    It takes in an array of tuples like [(src_1, dst_1), (src_2, dst_2), ..., (src_n, dst_n)]
    This method assumes all tuples have two elements and the sources and destinations are all unique
    """

    result: list[tuple[str, str]] = []

    # edges of the graphs ready to be processed
    queue: list[tuple[str, str]] = []
    # names still in use as a source, blocking any rename that targets them
    blockers: set[str] = set()
    # reverse index for ease of access
    dst_to_src: dict[str, str] = {}

    # Discard no-op renames before doing any work
    edges = [(src, dst) for src, dst in input_graph if src != dst]

    for src, dst in edges:
        blockers.add(src)
        dst_to_src[dst] = src

    pending = set(edges)

    # seed queue with renames whose destination is not a pending source
    for src, dst in edges:
        # if src == dst:
        #     pending.remove((src, dst))
        #     continue
        if dst not in blockers:
            queue.append((src, dst))

    def _release_src(src: str) -> None:
        """Mark src as consumed; enqueue the node targeting it if any."""
        blockers.discard(src)
        predecessor = dst_to_src.get(src)
        if predecessor is not None and (predecessor, src) in pending:
            queue.append((predecessor, src))

    # Kahn's algorithm(ish)
    def _drain_queue() -> None:
        while queue:
            src, dst = queue.pop()
            pending.remove((src, dst))
            result.append((src, dst))
            _release_src(src)

    _drain_queue()

    # The removing pairs are cycles, break them with a temp file
    while pending:
        # Pick any node in a cycle
        (src, dst) = next(iter(pending))
        tmp = f"{src}_tmp_sbr"

        result.append((src, tmp))
        pending.remove((src, dst))
        pending.add((tmp, dst))
        dst_to_src[dst] = tmp
        blockers.add(tmp)

        _release_src(src)

        # Also check if tmp's destination is now safe
        if dst not in blockers:
            queue.append((tmp, dst))

        _drain_queue()

    return result

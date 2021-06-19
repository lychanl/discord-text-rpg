from typing import Sequence


def split_message(message: str, limit: int) -> Sequence[str]:
    out = []

    if len(message) < limit:
        out.append(message)
    else:
        lines = message.splitlines()
        out.append(lines[0])
        for line in lines[1:]:
            if len(out[-1]) + len(line) + 1 < limit:
                out[-1] += out[-1] + '\n' + line
            else:
                out.append(line)

    return out


def split_messages(messages: Sequence[str], limit: int) -> Sequence[str]:
    if not messages:
        return None
    out = split_message(messages[0], limit)

    for msg in messages[1:]:
        if len(msg) + len(out[-1]) + 1 < limit:
            out[-1] = out[-1] + '\n' + msg
        else:
            if len(msg) < limit:
                out.append(msg)
            else:
                out.extend(split_message(msg, limit))

    return out

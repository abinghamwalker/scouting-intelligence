# Sole local W04 Wyscout runtime-control and build-identity launcher.  Direct
# execution enters the verifier below before any file-backed import.  Importing
# the module for its closed API has no product or filesystem side effects.
# This branch is the first executable launcher statement.  Direct imports used by
# unit tests skip it; the exact script invocation must complete this built-in-only
# bootstrap before the first further file-backed import below.
if __name__ == "__main__":
    _W04_STARTUP_SYSTEM = __import__("sys")
    _W04_STARTUP_MODULE_NAMES = (
        "sys",
        "builtins",
        "_frozen_importlib",
        "_imp",
        "_thread",
        "_warnings",
        "_weakref",
        "_io",
        "marshal",
        "posix",
        "_frozen_importlib_external",
        "time",
        "zipimport",
        "_codecs",
        "codecs",
        "encodings.aliases",
        "encodings",
        "encodings.utf_8",
        "_signal",
        "_abc",
        "abc",
        "io",
        "__main__",
    )
    if tuple(_W04_STARTUP_SYSTEM.modules) != _W04_STARTUP_MODULE_NAMES:
        raise RuntimeError("outer earliest resident module roster differs")
    _W04_STARTUP_MODULE_PAIRS = tuple(
        (name, _W04_STARTUP_SYSTEM.modules[name]) for name in _W04_STARTUP_MODULE_NAMES
    )
    _W04_STARTUP_BUILTIN_IMPORTER = getattr(
        _W04_STARTUP_SYSTEM.modules["_frozen_importlib"], "BuiltinImporter", None
    )
    _W04_STARTUP_FROZEN_IMPORTER = getattr(
        _W04_STARTUP_SYSTEM.modules["_frozen_importlib"], "FrozenImporter", None
    )
    _W04_STARTUP_BUILTIN_FROZEN_NAMES = (
        "sys",
        "builtins",
        "_frozen_importlib",
        "_imp",
        "_thread",
        "_warnings",
        "_weakref",
        "_io",
        "marshal",
        "posix",
        "_frozen_importlib_external",
        "time",
        "zipimport",
        "_codecs",
        "codecs",
        "_signal",
        "_abc",
        "abc",
        "io",
    )
    _W04_STARTUP_BUILTIN_FROZEN_SHAPES = tuple(
        (
            name,
            getattr(_W04_STARTUP_SYSTEM.modules[name], "__package__", None),
            getattr(getattr(_W04_STARTUP_SYSTEM.modules[name], "__spec__", None), "parent", None),
            (
                None
                if getattr(
                    getattr(_W04_STARTUP_SYSTEM.modules[name], "__spec__", None),
                    "submodule_search_locations",
                    None,
                )
                is None
                else tuple(
                    getattr(
                        getattr(_W04_STARTUP_SYSTEM.modules[name], "__spec__", None),
                        "submodule_search_locations",
                    )
                )
            ),
        )
        for name in _W04_STARTUP_BUILTIN_FROZEN_NAMES
    )

    def _w04_early_sha256(payload: bytes) -> str:
        """Return SHA-256 without importing a file-backed hashing module."""

        constants = (
            0x428A2F98,
            0x71374491,
            0xB5C0FBCF,
            0xE9B5DBA5,
            0x3956C25B,
            0x59F111F1,
            0x923F82A4,
            0xAB1C5ED5,
            0xD807AA98,
            0x12835B01,
            0x243185BE,
            0x550C7DC3,
            0x72BE5D74,
            0x80DEB1FE,
            0x9BDC06A7,
            0xC19BF174,
            0xE49B69C1,
            0xEFBE4786,
            0x0FC19DC6,
            0x240CA1CC,
            0x2DE92C6F,
            0x4A7484AA,
            0x5CB0A9DC,
            0x76F988DA,
            0x983E5152,
            0xA831C66D,
            0xB00327C8,
            0xBF597FC7,
            0xC6E00BF3,
            0xD5A79147,
            0x06CA6351,
            0x14292967,
            0x27B70A85,
            0x2E1B2138,
            0x4D2C6DFC,
            0x53380D13,
            0x650A7354,
            0x766A0ABB,
            0x81C2C92E,
            0x92722C85,
            0xA2BFE8A1,
            0xA81A664B,
            0xC24B8B70,
            0xC76C51A3,
            0xD192E819,
            0xD6990624,
            0xF40E3585,
            0x106AA070,
            0x19A4C116,
            0x1E376C08,
            0x2748774C,
            0x34B0BCB5,
            0x391C0CB3,
            0x4ED8AA4A,
            0x5B9CCA4F,
            0x682E6FF3,
            0x748F82EE,
            0x78A5636F,
            0x84C87814,
            0x8CC70208,
            0x90BEFFFA,
            0xA4506CEB,
            0xBEF9A3F7,
            0xC67178F2,
        )
        state = [
            0x6A09E667,
            0xBB67AE85,
            0x3C6EF372,
            0xA54FF53A,
            0x510E527F,
            0x9B05688C,
            0x1F83D9AB,
            0x5BE0CD19,
        ]
        length = len(payload)
        padded = payload + b"\x80"
        padded += bytes((-len(padded) - 8) % 64)
        padded += (length * 8).to_bytes(8, "big")
        mask = 0xFFFFFFFF

        def rotate(value: int, count: int) -> int:
            return ((value >> count) | (value << (32 - count))) & mask

        for start in range(0, len(padded), 64):
            block = padded[start : start + 64]
            words = [int.from_bytes(block[index : index + 4], "big") for index in range(0, 64, 4)]
            for index in range(16, 64):
                first = words[index - 15]
                second = words[index - 2]
                sigma0 = rotate(first, 7) ^ rotate(first, 18) ^ (first >> 3)
                sigma1 = rotate(second, 17) ^ rotate(second, 19) ^ (second >> 10)
                words.append((words[index - 16] + sigma0 + words[index - 7] + sigma1) & mask)
            a, b, c, d, e, f, g, h = state
            for index, constant in enumerate(constants):
                big1 = rotate(e, 6) ^ rotate(e, 11) ^ rotate(e, 25)
                choose = (e & f) ^ ((~e) & g)
                temporary1 = (h + big1 + choose + constant + words[index]) & mask
                big0 = rotate(a, 2) ^ rotate(a, 13) ^ rotate(a, 22)
                majority = (a & b) ^ (a & c) ^ (b & c)
                temporary2 = (big0 + majority) & mask
                h, g, f, e, d, c, b, a = (
                    g,
                    f,
                    e,
                    (d + temporary1) & mask,
                    c,
                    b,
                    a,
                    (temporary1 + temporary2) & mask,
                )
            state = [(left + right) & mask for left, right in zip(state, (a, b, c, d, e, f, g, h))]
        return b"".join(value.to_bytes(4, "big") for value in state).hex()

    def _w04_early_b64u_decode(value: str) -> bytes:
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
        if not value or "=" in value or len(value) % 4 == 1:
            raise RuntimeError("outer bootstrap base64url is malformed")
        table = {character: index for index, character in enumerate(alphabet)}
        accumulator = 0
        bits = 0
        output = bytearray()
        for character in value:
            if character not in table:
                raise RuntimeError("outer bootstrap base64url alphabet differs")
            accumulator = (accumulator << 6) | table[character]
            bits += 6
            while bits >= 8:
                bits -= 8
                output.append((accumulator >> bits) & 0xFF)
        if bits and accumulator & ((1 << bits) - 1):
            raise RuntimeError("outer bootstrap base64url padding bits differ")
        groups = (len(output) * 8 + 5) // 6
        encoded_value = int.from_bytes(output, "big") << (groups * 6 - len(output) * 8)
        encoded = "".join(
            alphabet[(encoded_value >> shift) & 63] for shift in range((groups - 1) * 6, -1, -6)
        )
        if encoded != value:
            raise RuntimeError("outer bootstrap base64url is not canonical")
        return bytes(output)

    def _w04_early_json(raw: bytes) -> object:
        """Parse the closed ASCII canonical-JSON subset used by the bootstrap."""

        try:
            text = raw.decode("ascii", errors="strict")
        except UnicodeDecodeError as error:
            raise RuntimeError("outer bootstrap JSON is not closed ASCII") from error
        position = 0

        def parse_string() -> str:
            nonlocal position
            if position >= len(text) or text[position] != '"':
                raise RuntimeError("outer bootstrap JSON string is malformed")
            position += 1
            output: list[str] = []
            escapes = {'"': '"', "\\": "\\", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t"}
            while position < len(text):
                character = text[position]
                position += 1
                if character == '"':
                    return "".join(output)
                if character == "\\":
                    if position >= len(text) or text[position] not in escapes:
                        raise RuntimeError("outer bootstrap JSON escape is malformed")
                    output.append(escapes[text[position]])
                    position += 1
                elif ord(character) < 0x20:
                    raise RuntimeError("outer bootstrap JSON contains a control character")
                else:
                    output.append(character)
            raise RuntimeError("outer bootstrap JSON string is unterminated")

        def parse_value() -> object:
            nonlocal position
            if position >= len(text):
                raise RuntimeError("outer bootstrap JSON ended early")
            character = text[position]
            if character == '"':
                return parse_string()
            if character == "[":
                position += 1
                values: list[object] = []
                if position < len(text) and text[position] == "]":
                    position += 1
                    return values
                while True:
                    values.append(parse_value())
                    if position >= len(text):
                        raise RuntimeError("outer bootstrap JSON array ended early")
                    separator = text[position]
                    position += 1
                    if separator == "]":
                        return values
                    if separator != ",":
                        raise RuntimeError("outer bootstrap JSON array separator differs")
            if character == "{":
                position += 1
                object_value: dict[str, object] = {}
                if position < len(text) and text[position] == "}":
                    position += 1
                    return object_value
                while True:
                    key = parse_string()
                    if key in object_value or position >= len(text) or text[position] != ":":
                        raise RuntimeError("outer bootstrap JSON object key differs")
                    position += 1
                    object_value[key] = parse_value()
                    if position >= len(text):
                        raise RuntimeError("outer bootstrap JSON object ended early")
                    separator = text[position]
                    position += 1
                    if separator == "}":
                        return object_value
                    if separator != ",":
                        raise RuntimeError("outer bootstrap JSON object separator differs")
            for literal, literal_value in (
                ("true", True),
                ("false", False),
                ("null", None),
            ):
                if text.startswith(literal, position):
                    position += len(literal)
                    return literal_value
            start = position
            if character == "0":
                position += 1
            elif "1" <= character <= "9":
                position += 1
                while position < len(text) and text[position].isdigit():
                    position += 1
            else:
                raise RuntimeError("outer bootstrap JSON value differs")
            return int(text[start:position])

        result = parse_value()
        if position != len(text):
            raise RuntimeError("outer bootstrap JSON has trailing bytes")
        return result

    def _w04_early_json_bytes(value: object) -> bytes:
        if value is True:
            return b"true"
        if value is False:
            return b"false"
        if value is None:
            return b"null"
        if type(value) is int and value >= 0:
            return str(value).encode("ascii")
        if type(value) is str:
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            escaped = (
                escaped.replace("\b", "\\b")
                .replace("\f", "\\f")
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t")
            )
            return b'"' + escaped.encode("ascii", errors="strict") + b'"'
        if type(value) is list:
            return b"[" + b",".join(_w04_early_json_bytes(item) for item in value) + b"]"
        if type(value) is dict and all(type(key) is str for key in value):
            return (
                b"{"
                + b",".join(
                    _w04_early_json_bytes(key) + b":" + _w04_early_json_bytes(value[key])
                    for key in sorted(value)
                )
                + b"}"
            )
        raise RuntimeError("outer bootstrap JSON contains an unsupported value")

    def _w04_early_read(posix_module: "Any", descriptor: int, size: int) -> bytes:
        chunks: list[bytes] = []
        offset = 0
        while offset < size:
            chunk = posix_module.pread(descriptor, min(1024 * 1024, size - offset), offset)
            if not chunk:
                raise RuntimeError("outer bootstrap source ended early")
            chunks.append(chunk)
            offset += len(chunk)
        if posix_module.pread(descriptor, 1, size) != b"":
            raise RuntimeError("outer bootstrap source lacks exact EOF")
        return b"".join(chunks)

    def _w04_early_stat_snapshot(metadata: "Any") -> tuple[int, ...]:
        """Capture every stable security-relevant identity field used pre-guard."""

        return (
            metadata.st_dev,
            metadata.st_ino,
            metadata.st_mode,
            metadata.st_nlink,
            metadata.st_uid,
            metadata.st_gid,
            metadata.st_size,
            metadata.st_mtime_ns,
            metadata.st_ctime_ns,
        )

    def _w04_early_bootstrap() -> dict[str, object]:
        system = __import__("sys")
        posix_module = __import__("posix")
        __import__("_io")
        environment = {
            key.decode("utf-8", errors="strict"): value.decode("utf-8", errors="strict")
            for key, value in posix_module.environ.items()
        }
        tuple_value = environment.get("W04_BOOTSTRAP_TUPLE_B64", "")
        tuple_raw = _w04_early_b64u_decode(tuple_value)
        bootstrap_tuple = _w04_early_json(tuple_raw)
        if type(bootstrap_tuple) is not dict or _w04_early_json_bytes(bootstrap_tuple) != tuple_raw:
            raise RuntimeError("outer bootstrap tuple is not one canonical object")

        project_root = posix_module.getcwd()
        outer_argv = [
            "uv",
            "run",
            "--locked",
            "--no-sync",
            "python",
            "-S",
            "-B",
            "scripts/launch_wyscout_v5.py",
        ]
        source_fd_text = environment.get("W04_LAUNCHER_SOURCE_FD", "")
        if (
            not source_fd_text.isdecimal()
            or source_fd_text.startswith("0")
            or int(source_fd_text) < 3
            or int(source_fd_text) > 2_147_483_647
        ):
            raise RuntimeError("outer launcher source descriptor spelling differs")
        source_fd = int(source_fd_text)
        control_prefix = environment.get("PYTHONPYCACHEPREFIX", "")
        prefix_lead = project_root + "/data/working/wyscout/v5/.staging/control/control_run_id="
        prefix_tail = "/runtime-pycache"
        if not control_prefix.startswith(prefix_lead) or not control_prefix.endswith(prefix_tail):
            raise RuntimeError("outer control-prefix spelling differs")
        control_run_id = control_prefix[len(prefix_lead) : -len(prefix_tail)]
        uuid_shape = (8, 13, 18, 23)
        if (
            len(control_run_id) != 36
            or any(control_run_id[index] != "-" for index in uuid_shape)
            or any(
                character not in "0123456789abcdef"
                for index, character in enumerate(control_run_id)
                if index not in uuid_shape
            )
            or control_run_id[14] != "4"
            or control_run_id[19] not in "89ab"
        ):
            raise RuntimeError("outer control run ID is not canonical UUIDv4")

        literals = {
            "ARROW_NUM_THREADS": "1",
            "LANG": "C",
            "LC_ALL": "C",
            "MKL_NUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1",
            "OMP_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "POLARS_MAX_THREADS": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0",
            "PYTHONIOENCODING": "utf-8:strict",
            "PYTHONNOUSERSITE": "1",
            "PYTHONUTF8": "1",
            "RAYON_NUM_THREADS": "1",
            "TZ": "UTC",
            "UV_LOCKED": "1",
            "UV_NO_SYNC": "1",
            "UV_OFFLINE": "1",
            "UV_RUN_RECURSION_DEPTH": "1",
            "VECLIB_MAXIMUM_THREADS": "1",
        }
        operational = {
            "HOME": "/Users/adrian",
            "PATH": project_root + "/.venv/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin",
            "PYTHONPYCACHEPREFIX": control_prefix,
            "TMPDIR": "/var/folders/8r/chc2bb390r9cw7s2m65b21h80000gn/T/",
            "UV": "/opt/homebrew/bin/uv",
            "UV_CACHE_DIR": "/Users/adrian/.cache/uv",
            "VIRTUAL_ENV": project_root + "/.venv",
            "W04_LAUNCHER_SOURCE_FD": source_fd_text,
            "__CF_USER_TEXT_ENCODING": "0x1F5:0:2",
        }
        expected_environment = {**literals, **operational, "W04_BOOTSTRAP_TUPLE_B64": tuple_value}
        if environment != expected_environment:
            raise RuntimeError("outer transport environment is not the exact closed map")
        tokens = {
            "HOME": "<W04_HOME>",
            "PATH": "<W04_VENV_BIN>:<W04_UV_BIN_DIR>:/usr/bin:/bin:/usr/sbin:/sbin",
            "PYTHONPYCACHEPREFIX": "<CONTROL_PREFIX>",
            "TMPDIR": "<W04_TMPDIR>",
            "UV": "<W04_UV_LOGICAL_LAUNCH_PATH>",
            "UV_CACHE_DIR": "<W04_UV_CACHE_ROOT>",
            "VIRTUAL_ENV": "<W04_PROJECT_ROOT>/.venv",
            "W04_LAUNCHER_SOURCE_FD": "<LAUNCHER_SOURCE_FD>",
            "__CF_USER_TEXT_ENCODING": "<W04_CF_USER_TEXT_ENCODING>",
        }
        normalized = {**literals, **{key: tokens[key] for key in operational}}
        absent = [
            "ALL_PROXY",
            "COVERAGE_PROCESS_CONFIG",
            "COVERAGE_PROCESS_START",
            "DYLD_FALLBACK_FRAMEWORK_PATH",
            "DYLD_FALLBACK_LIBRARY_PATH",
            "DYLD_FRAMEWORK_PATH",
            "DYLD_INSERT_LIBRARIES",
            "DYLD_LIBRARY_PATH",
            "HTTP_PROXY",
            "HTTPS_PROXY",
            "LD_LIBRARY_PATH",
            "LD_PRELOAD",
            "NO_PROXY",
            "PYTHONBREAKPOINT",
            "PYTHONHOME",
            "PYTHONINSPECT",
            "PYTHONOPTIMIZE",
            "PYTHONPATH",
            "PYTHONSTARTUP",
            "PYTHONUSERBASE",
            "PYTHONWARNINGS",
            "UV_DEFAULT_INDEX",
            "UV_EXTRA_INDEX_URL",
            "UV_FIND_LINKS",
            "UV_INDEX",
            "UV_PROJECT_ENVIRONMENT",
            "UV_PYTHON",
            "UV_PYTHON_PREFERENCE",
            "W04_BOOTSTRAP_TUPLE_B64",
            "W04_CHILD_INPUT_B64",
            "W04_CHILD_ROLE",
            "W04_ENTRYPOINT_SOURCE_FD",
            "W04_RESULT_FD",
            "W04_RESULT_NONCE",
            "all_proxy",
            "http_proxy",
            "https_proxy",
            "no_proxy",
        ]
        environment_authority = {
            "algorithm": "w04-outer-environment-bootstrap-v2",
            "excluded_until_insertion": ["W04_BOOTSTRAP_TUPLE_B64"],
            "present": {key: normalized[key] for key in sorted(normalized)},
            "required_absent": sorted(absent),
        }
        fixed_environment_digest = _w04_early_sha256(_w04_early_json_bytes(environment_authority))

        maximum_fd = min(int(posix_module.sysconf("SC_OPEN_MAX")), 65_536)
        open_fds = []
        for descriptor in range(maximum_fd):
            try:
                posix_module.fstat(descriptor)
            except OSError:
                continue
            open_fds.append(descriptor)
        if open_fds != [0, 1, 2, source_fd]:
            raise RuntimeError("outer inherited descriptor census differs")
        before = posix_module.fstat(source_fd)
        launcher_path = project_root + "/scripts/launch_wyscout_v5.py"
        path_metadata = posix_module.stat(launcher_path, follow_symlinks=False)
        if (
            before.st_mode & 0o170000 != 0o100000
            or before.st_mode & 0o777 != 0o644
            or before.st_nlink != 1
            or posix_module.lseek(source_fd, 0, 1) != 0
            or not posix_module.get_inheritable(source_fd)
            or (
                path_metadata.st_dev,
                path_metadata.st_ino,
                path_metadata.st_mode,
                path_metadata.st_nlink,
                path_metadata.st_size,
            )
            != (
                before.st_dev,
                before.st_ino,
                before.st_mode,
                before.st_nlink,
                before.st_size,
            )
        ):
            raise RuntimeError("outer launcher source descriptor metadata differs")
        launcher_raw = _w04_early_read(posix_module, source_fd, before.st_size)
        after = posix_module.fstat(source_fd)
        launcher_digest = _w04_early_sha256(launcher_raw)
        if (before.st_dev, before.st_ino, before.st_mode, before.st_nlink, before.st_size) != (
            after.st_dev,
            after.st_ino,
            after.st_mode,
            after.st_nlink,
            after.st_size,
        ) or posix_module.lseek(source_fd, 0, 1) != 0:
            raise RuntimeError("outer launcher source descriptor drifted")

        encoding_rows = [
            {
                "module": "encodings",
                "path": "encodings/__init__.py",
                "sha256": "78c4744d407690f321565488710b5aaf6486b5afa8d185637aa1e7633ab59cd8",
                "size_bytes": 5_884,
            },
            {
                "module": "encodings.aliases",
                "path": "encodings/aliases.py",
                "sha256": "6fdcc49ba23a0203ae6cf28e608f8e6297d7c4d77d52e651db3cb49b9564c6d2",
                "size_bytes": 15_677,
            },
            {
                "module": "encodings.utf_8",
                "path": "encodings/utf_8.py",
                "sha256": "ba0cac060269583523ca9506473a755203037c57d466a11aa89a30a5f6756f3d",
                "size_bytes": 1_005,
            },
        ]
        stdlib_root = system.base_prefix + "/lib/python3.12"

        expected_encoding_sources = {
            row["module"]: stdlib_root + "/" + row["path"] for row in encoding_rows
        }
        expected_module_names = (
            "sys",
            "builtins",
            "_frozen_importlib",
            "_imp",
            "_thread",
            "_warnings",
            "_weakref",
            "_io",
            "marshal",
            "posix",
            "_frozen_importlib_external",
            "time",
            "zipimport",
            "_codecs",
            "codecs",
            "encodings.aliases",
            "encodings",
            "encodings.utf_8",
            "_signal",
            "_abc",
            "abc",
            "io",
            "__main__",
        )
        if tuple(system.modules) != expected_module_names:
            raise RuntimeError("outer pre-guard resident module roster differs")
        if expected_module_names != _W04_STARTUP_MODULE_NAMES or len(
            _W04_STARTUP_MODULE_PAIRS
        ) != len(expected_module_names):
            raise RuntimeError("outer earliest resident module roster binding differs")
        live_module_pairs = tuple(system.modules.items())
        if any(
            live_name != startup_name or live_module is not startup_module
            for (live_name, live_module), (startup_name, startup_module) in zip(
                live_module_pairs, _W04_STARTUP_MODULE_PAIRS, strict=True
            )
        ):
            raise RuntimeError("outer resident startup object binding differs")
        module_objects = tuple(system.modules[name] for name in expected_module_names)
        if any(module is None for module in module_objects) or len(
            {id(module) for module in module_objects}
        ) != len(module_objects):
            raise RuntimeError("outer pre-guard resident module identity census differs")

        builtin_names = system.builtin_module_names
        frozen_importlib = system.modules["_frozen_importlib"]
        frozen_external = system.modules["_frozen_importlib_external"]
        frozen_authority = system.modules["_imp"]
        builtin_importer = getattr(frozen_importlib, "BuiltinImporter", None)
        frozen_importer = getattr(frozen_importlib, "FrozenImporter", None)
        source_file_loader = getattr(frozen_external, "SourceFileLoader", None)
        builtin_rows = {
            "sys",
            "builtins",
            "_imp",
            "_thread",
            "_warnings",
            "_weakref",
            "_io",
            "marshal",
            "posix",
            "time",
            "_codecs",
            "_signal",
            "_abc",
        }
        frozen_rows = {
            "_frozen_importlib": None,
            "_frozen_importlib_external": stdlib_root + "/importlib/_bootstrap_external.py",
            "zipimport": stdlib_root + "/zipimport.py",
            "codecs": stdlib_root + "/codecs.py",
            "abc": stdlib_root + "/abc.py",
            "io": stdlib_root + "/io.py",
        }
        if (
            type(builtin_names) is not tuple
            or type(builtin_importer) is not type
            or type(frozen_importer) is not type
            or type(source_file_loader) is not type
            or getattr(frozen_authority, "is_frozen", None) is None
            or builtin_importer is not _W04_STARTUP_BUILTIN_IMPORTER
            or frozen_importer is not _W04_STARTUP_FROZEN_IMPORTER
        ):
            raise RuntimeError("outer resident importer authority differs")
        startup_shapes = {
            name: (package, parent, locations)
            for name, package, parent, locations in _W04_STARTUP_BUILTIN_FROZEN_SHAPES
        }
        if tuple(startup_shapes) != _W04_STARTUP_BUILTIN_FROZEN_NAMES or any(
            type(package) is not str
            or package != ""
            or type(parent) is not str
            or parent != ""
            or locations is not None
            for package, parent, locations in startup_shapes.values()
        ):
            raise RuntimeError("outer earliest built-in/frozen shape binding differs")

        for module_name, module in system.modules.items():
            if type(module_name) is not str or module is None:
                raise RuntimeError("outer pre-guard resident module census differs")
            specification = getattr(module, "__spec__", None)
            origin = getattr(specification, "origin", None)
            module_file = getattr(module, "__file__", None)
            module_cached = getattr(module, "__cached__", None)
            module_loader = getattr(module, "__loader__", None)
            raw_locations = getattr(specification, "submodule_search_locations", None)
            current_shape = (
                getattr(module, "__package__", None),
                getattr(specification, "parent", None),
                None if raw_locations is None else tuple(raw_locations),
            )
            if getattr(module, "__name__", None) != module_name:
                raise RuntimeError("outer pre-guard resident module name differs")
            if module_name in builtin_rows:
                if (
                    current_shape != startup_shapes[module_name]
                    or type(current_shape[0]) is not str
                    or current_shape[0] != ""
                    or type(current_shape[1]) is not str
                    or current_shape[1] != ""
                    or current_shape[2] is not None
                    or module_name not in builtin_names
                    or specification is None
                    or getattr(specification, "name", None) != module_name
                    or origin != "built-in"
                    or getattr(specification, "loader", None) is not builtin_importer
                    or module_loader is not builtin_importer
                    or getattr(specification, "cached", None) is not None
                    or getattr(specification, "has_location", None) is not False
                    or module_file is not None
                    or module_cached is not None
                ):
                    raise RuntimeError("outer pre-guard built-in module authority differs")
            elif module_name in frozen_rows:
                if (
                    current_shape != startup_shapes[module_name]
                    or type(current_shape[0]) is not str
                    or current_shape[0] != ""
                    or type(current_shape[1]) is not str
                    or current_shape[1] != ""
                    or current_shape[2] is not None
                    or not frozen_authority.is_frozen(module_name)
                    or specification is None
                    or getattr(specification, "name", None) != module_name
                    or origin != "frozen"
                    or getattr(specification, "loader", None) is not frozen_importer
                    or module_loader is not frozen_importer
                    or getattr(specification, "cached", None) is not None
                    or getattr(specification, "has_location", None) is not False
                    or module_file != frozen_rows[module_name]
                    or module_cached is not None
                ):
                    raise RuntimeError("outer pre-guard frozen module authority differs")
            elif module_name in expected_encoding_sources:
                expected_source = expected_encoding_sources[module_name]
                expected_cached = control_prefix + expected_source[:-3] + ".cpython-312.pyc"
                loader = getattr(specification, "loader", None)
                expected_locations = (
                    [stdlib_root + "/encodings"] if module_name == "encodings" else None
                )
                if (
                    specification is None
                    or getattr(specification, "name", None) != module_name
                    or origin != expected_source
                    or module_file != expected_source
                    or type(loader) is not source_file_loader
                    or module_loader is not loader
                    or getattr(loader, "name", None) != module_name
                    or getattr(loader, "path", None) != expected_source
                    or getattr(specification, "cached", None) != expected_cached
                    or module_cached != expected_cached
                    or getattr(specification, "has_location", None) is not True
                    or getattr(specification, "parent", None) != "encodings"
                    or getattr(specification, "submodule_search_locations", None)
                    != expected_locations
                    or getattr(module, "__package__", None) != "encodings"
                ):
                    raise RuntimeError("outer pre-guard encoding module census differs")
            elif module_name == "__main__" and module is system.modules.get("__main__"):
                main_loader = getattr(module, "__loader__", None)
                if (
                    specification is not None
                    or module_file != launcher_path
                    or module_cached is not None
                    or type(main_loader) is not source_file_loader
                    or getattr(main_loader, "name", None) != "__main__"
                    or getattr(main_loader, "path", None) != launcher_path
                    or getattr(module, "__package__", None) is not None
                ):
                    raise RuntimeError("outer pre-guard __main__ module differs")
            else:
                raise RuntimeError("outer pre-guard resident module roster differs")

        for row in encoding_rows:
            module = system.modules.get(row["module"])
            source = stdlib_root + "/" + row["path"]
            specification = getattr(module, "__spec__", None)
            if (
                module is None
                or getattr(specification, "origin", None) != source
                or getattr(module, "__file__", None) != source
            ):
                raise RuntimeError("outer encoding source origin differs")
            cached = getattr(module, "__cached__", None)
            if type(cached) is not str or not cached.startswith(control_prefix + "/"):
                raise RuntimeError("outer encoding cache candidate differs")
            try:
                posix_module.stat(cached, follow_symlinks=False)
            except FileNotFoundError:
                pass
            else:
                raise RuntimeError("outer encoding cache candidate exists")

        directory_only_flag = getattr(posix_module, "O_DIRECTORY", 0)
        no_follow_flag = getattr(posix_module, "O_NOFOLLOW", 0)
        if not directory_only_flag or not no_follow_flag:
            raise RuntimeError("outer no-follow directory capability is unavailable")
        directory_flags = 0 | directory_only_flag | no_follow_flag
        if (
            type(system.base_prefix) is not str
            or not system.base_prefix.startswith("/")
            or system.base_prefix.endswith("/")
        ):
            raise RuntimeError("outer stdlib root spelling differs")
        stdlib_parts = stdlib_root.split("/")
        if stdlib_parts[0] != "" or any(
            not part or part in (".", "..") or "/" in part for part in stdlib_parts[1:]
        ):
            raise RuntimeError("outer stdlib root spelling differs")

        current_uid = posix_module.getuid()
        current_gid = posix_module.getgid()
        directory_descriptors = []
        directory_bindings = []
        source_descriptors = []
        source_bindings = []
        try:
            root_descriptor = posix_module.open("/", directory_flags)
            directory_descriptors.append(root_descriptor)
            root_snapshot = _w04_early_stat_snapshot(posix_module.fstat(root_descriptor))
            root_path_snapshot = _w04_early_stat_snapshot(
                posix_module.stat("/", follow_symlinks=False)
            )
            if (
                root_snapshot != root_path_snapshot
                or root_snapshot[2] & 0o170000 != 0o040000
                or root_snapshot[2] & 0o022
            ):
                raise RuntimeError("outer stdlib descriptor chain is unsafe")
            parent_descriptor = root_descriptor
            owner_transitioned = root_snapshot[4] == current_uid
            for part in stdlib_parts[1:]:
                path_metadata = posix_module.stat(
                    part, dir_fd=parent_descriptor, follow_symlinks=False
                )
                path_snapshot = _w04_early_stat_snapshot(path_metadata)
                child_descriptor = posix_module.open(
                    part, directory_flags, dir_fd=parent_descriptor
                )
                directory_descriptors.append(child_descriptor)
                child_snapshot = _w04_early_stat_snapshot(posix_module.fstat(child_descriptor))
                if (
                    path_snapshot != child_snapshot
                    or child_snapshot[2] & 0o170000 != 0o040000
                    or child_snapshot[2] & 0o022
                    or child_snapshot[4] not in (0, current_uid)
                    or (owner_transitioned and child_snapshot[4] != current_uid)
                ):
                    raise RuntimeError("outer stdlib descriptor chain is unsafe")
                if child_snapshot[4] == current_uid:
                    owner_transitioned = True
                directory_bindings.append(
                    (parent_descriptor, part, child_descriptor, child_snapshot)
                )
                parent_descriptor = child_descriptor
            stdlib_descriptor = parent_descriptor
            stdlib_snapshot = directory_bindings[-1][3]
            if (
                stdlib_snapshot[2] & 0o777 != 0o755
                or stdlib_snapshot[4] != current_uid
                or stdlib_snapshot[5] != current_gid
            ):
                raise RuntimeError("outer stdlib owner or mode differs")

            encodings_path_metadata = posix_module.stat(
                "encodings", dir_fd=stdlib_descriptor, follow_symlinks=False
            )
            encodings_path_snapshot = _w04_early_stat_snapshot(encodings_path_metadata)
            encodings_descriptor = posix_module.open(
                "encodings", directory_flags, dir_fd=stdlib_descriptor
            )
            directory_descriptors.append(encodings_descriptor)
            encodings_snapshot = _w04_early_stat_snapshot(posix_module.fstat(encodings_descriptor))
            if (
                encodings_path_snapshot != encodings_snapshot
                or encodings_snapshot[2] & 0o170000 != 0o040000
                or encodings_snapshot[2] & 0o777 != 0o755
                or encodings_snapshot[4] != current_uid
                or encodings_snapshot[5] != current_gid
            ):
                raise RuntimeError("outer encoding parent owner, mode, or identity differs")
            directory_bindings.append(
                (stdlib_descriptor, "encodings", encodings_descriptor, encodings_snapshot)
            )

            for row in encoding_rows:
                relative = row["path"]
                if type(relative) is not str or not relative.startswith("encodings/"):
                    raise RuntimeError("outer encoding source path authority differs")
                leaf = relative[len("encodings/") :]
                if not leaf or leaf in (".", "..") or "/" in leaf:
                    raise RuntimeError("outer encoding source escaped its admitted parent")
                leaf_path_metadata = posix_module.stat(
                    leaf, dir_fd=encodings_descriptor, follow_symlinks=False
                )
                leaf_path_snapshot = _w04_early_stat_snapshot(leaf_path_metadata)
                source_descriptor = posix_module.open(
                    leaf,
                    0 | no_follow_flag,
                    dir_fd=encodings_descriptor,
                )
                source_descriptors.append(source_descriptor)
                source_snapshot = _w04_early_stat_snapshot(posix_module.fstat(source_descriptor))
                if leaf_path_snapshot != source_snapshot:
                    raise RuntimeError("outer encoding source identity differs")
                size_bytes = row["size_bytes"]
                if type(size_bytes) is not int:
                    raise RuntimeError("outer encoding source size authority differs")
                if (
                    source_snapshot[2] & 0o170000 != 0o100000
                    or source_snapshot[2] & 0o777 != 0o644
                    or source_snapshot[3] != 1
                    or source_snapshot[4] != current_uid
                    or source_snapshot[5] != current_gid
                    or source_snapshot[6] != size_bytes
                ):
                    raise RuntimeError("outer encoding source owner or metadata differs")
                raw = _w04_early_read(posix_module, source_descriptor, size_bytes)
                if _w04_early_sha256(raw) != row["sha256"]:
                    raise RuntimeError("outer encoding source bytes differ")
                source_bindings.append((leaf, source_descriptor, source_snapshot, row["module"]))

            for leaf, source_descriptor, source_snapshot, _module_name in source_bindings:
                if (
                    _w04_early_stat_snapshot(posix_module.fstat(source_descriptor))
                    != source_snapshot
                    or _w04_early_stat_snapshot(
                        posix_module.stat(leaf, dir_fd=encodings_descriptor, follow_symlinks=False)
                    )
                    != source_snapshot
                ):
                    raise RuntimeError("outer encoding source identity drifted")
            for (
                bound_parent,
                bound_name,
                bound_descriptor,
                bound_snapshot,
            ) in directory_bindings:
                if (
                    _w04_early_stat_snapshot(posix_module.fstat(bound_descriptor)) != bound_snapshot
                    or _w04_early_stat_snapshot(
                        posix_module.stat(bound_name, dir_fd=bound_parent, follow_symlinks=False)
                    )
                    != bound_snapshot
                ):
                    raise RuntimeError("outer encoding parent identity drifted")
            if (
                _w04_early_stat_snapshot(posix_module.fstat(root_descriptor)) != root_snapshot
                or _w04_early_stat_snapshot(posix_module.stat("/", follow_symlinks=False))
                != root_snapshot
            ):
                raise RuntimeError("outer stdlib root identity drifted")
        except OSError as error:
            raise RuntimeError("outer stdlib no-follow descriptor traversal failed") from error
        finally:
            for descriptor in reversed(source_descriptors):
                posix_module.close(descriptor)
            for descriptor in reversed(directory_descriptors):
                posix_module.close(descriptor)

        prefix_metadata = posix_module.stat(control_prefix, follow_symlinks=False)
        if (
            prefix_metadata.st_mode & 0o170000 != 0o040000
            or prefix_metadata.st_mode & 0o777 != 0o700
            or posix_module.listdir(control_prefix)
        ):
            raise RuntimeError("outer control prefix is unsafe or nonempty")
        expected_tuple = {
            "control_prefix_policy": "w04-three-role-runtime-pycache-v1",
            "control_prefix_relative_template": (
                "data/working/wyscout/v5/.staging/control/control_run_id=<uuid>/runtime-pycache/"
            ),
            "encoding_source_rows": encoding_rows,
            "fixed_environment_algorithm": "w04-outer-environment-bootstrap-v2",
            "fixed_environment_digest": fixed_environment_digest,
            "launcher_mode": 0o644,
            "launcher_relative_path": "scripts/launch_wyscout_v5.py",
            "launcher_sha256": launcher_digest,
            "launcher_size": len(launcher_raw),
            "launcher_source_descriptor_policy": "w04-inherited-source-fd-v1",
            "ordered_argv": outer_argv,
            "process_role": "W04_LOCAL_CONTROL",
            "pyproject_sha256": "963db0004a52d36097bb66d7b5893044e7ac706580b14bae9e7e70e12ce5a89b",
            "python_physical_mode": 0o755,
            "python_physical_sha256": (
                "cf450e6bc0b00adecd12b7b13024de7000c7350801addc802bd3b45782104e79"
            ),
            "python_physical_size": 49_968,
            "python_version": "3.12.12",
            "uv_host_spelling_normalization": "w04-uv-host-spelling-normalization-v1",
            "uv_final_entry_kind": "regular_non_symlink_executable",
            "uv_installation_root_role": "<W04_UV_INSTALLATION_ROOT>",
            "uv_link_policy": "w04-uv-logical-one-hop-relative-link-v1",
            "uv_logical_entry_kind": "symlink",
            "uv_logical_launch_role": "<W04_UV_LOGICAL_LAUNCH>",
            "uv_physical_executable_role": "<W04_UV_PHYSICAL_EXECUTABLE>",
            "uv_physical_mode": 0o555,
            "uv_physical_sha256": (
                "4f0c0c002bb4702c1bd6792edc15f7ae3948b5f19509c8d73cd5c9a26298097f"
            ),
            "uv_physical_size": 41_617_552,
            "uv_raw_target_form": "relative_nonempty_nul_free_posix",
            "uv_raw_target_must_not_be_absolute": True,
            "uv_resolution_containment": "W04_UV_INSTALLATION_ROOT",
            "uv_resolution_hops": 1,
            "uv_version": "uv 0.9.21 (Homebrew 2025-12-30)",
            "uv_lock_sha256": "1c4d3408f3fd900443356f8387a1fed3554f9e0b69e74d9997cd99b60be134ca",
            "working_directory": "<W04_PROJECT_ROOT>",
        }
        if bootstrap_tuple != expected_tuple:
            received_keys = set(bootstrap_tuple) if type(bootstrap_tuple) is dict else set()
            expected_keys = set(expected_tuple)
            differing = sorted(
                key
                for key in received_keys & expected_keys
                if bootstrap_tuple[key] != expected_tuple[key]
            )
            raise RuntimeError(
                "outer bootstrap tuple differs from complete v4 authority: "
                f"missing={sorted(expected_keys - received_keys)!r}, "
                f"extra={sorted(received_keys - expected_keys)!r}, differing={differing!r}"
            )
        expected_python = project_root + "/.venv/bin/python3"
        if (
            system.argv != ["scripts/launch_wyscout_v5.py"]
            or system.orig_argv != [expected_python, "-S", "-B", "scripts/launch_wyscout_v5.py"]
            or system.executable != expected_python
            or system.version_info[:3] != (3, 12, 12)
            or not system.dont_write_bytecode
        ):
            raise RuntimeError("outer cwd/argv/interpreter projection differs")

        audit_rows: list[str] = []

        def audit_guard(event: str, arguments: "Any") -> None:
            if event == "open" and arguments:
                target = arguments[0]
                if type(target) is bytes:
                    target = target.decode("utf-8", errors="strict")
                if type(target) is str:
                    if target.lower().endswith((".pyc", ".pyo")) and not (
                        target == control_prefix or target.startswith(control_prefix + "/")
                    ):
                        raise RuntimeError("outer guard denied in-place bytecode access")
                    if target == control_prefix or target.startswith(control_prefix + "/"):
                        mode = arguments[1] if len(arguments) > 1 else None
                        flags = arguments[2] if len(arguments) > 2 else 0
                        if (
                            type(mode) is str
                            and any(token in mode for token in ("w", "a", "x", "+"))
                        ) or (type(flags) is int and flags & (1 | 2 | 64 | 512 | 1024)):
                            raise RuntimeError("outer guard denied a control-prefix write")
                audit_rows.append(event)

        system.addaudithook(audit_guard)
        posix_module.set_inheritable(source_fd, False)
        if posix_module.get_inheritable(source_fd):
            raise RuntimeError("outer launcher descriptor did not restore close-on-exec")
        return {
            "audit_rows": audit_rows,
            "bootstrap_tuple": bootstrap_tuple,
            "control_identity": (
                prefix_metadata.st_dev,
                prefix_metadata.st_ino,
                prefix_metadata.st_mode,
                prefix_metadata.st_nlink,
            ),
            "control_prefix": control_prefix,
            "control_run_id": control_run_id,
            "environment_sha256": _w04_early_sha256(
                _w04_early_json_bytes({key: environment[key] for key in sorted(environment)})
            ),
            "launcher_identity": (
                before.st_dev,
                before.st_ino,
                before.st_mode,
                before.st_nlink,
                before.st_size,
            ),
            "launcher_sha256": launcher_digest,
            "launcher_source_fd": source_fd,
            "project_root": project_root,
        }

    try:
        _W04_EARLY_BOOTSTRAP = _w04_early_bootstrap()
    except BaseException:
        _w04_posix = __import__("posix")
        _w04_fd_raw = _w04_posix.environ.get(b"W04_LAUNCHER_SOURCE_FD", b"")
        if _w04_fd_raw.isdigit():
            try:
                _w04_posix.close(int(_w04_fd_raw))
            except OSError:
                pass
        raise
else:
    _W04_EARLY_BOOTSTRAP = None  # type: ignore[assignment]

import base64
import configparser
import csv
import hashlib
import importlib.machinery
import json
import os
import re
import secrets
import selectors
import stat

# Subprocess is restricted below to the exact frozen tuple; shell is never used.
import subprocess  # nosec B404
import sys
import sysconfig
import time
import tomllib
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any, Final, cast
from unicodedata import is_normalized
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from scouting.contracts.wyscout_build import (
        ChildResultEnvelope,
        PreBuildAdmissionResult,
        RebuildInvocation,
    )

ADMISSION_ARGV: Final = (
    "uv",
    "run",
    "--locked",
    "--no-sync",
    "python",
    "-S",
    "-B",
    "scripts/admit_wyscout_v5_runtime.py",
)
REBUILD_ARGV: Final = (*ADMISSION_ARGV[:-1], "scripts/rebuild_wyscout_v5.py")
OUTER_ARGV: Final = (*ADMISSION_ARGV[:-1], "scripts/launch_wyscout_v5.py")
COMPONENT_KEYS: Final = (
    "child_result_contract_digest",
    "editable_root_digest",
    "environment_values_digest",
    "executable_census_digest",
    "extracted_runtime_digest",
    "installed_record_runtime_digest",
    "interpreter_digest",
    "local_launcher_control_digest",
    "local_resource_digest",
    "lock_inputs_digest",
    "process_launch_contract_digest",
    "pyc_policy_source_map_digest",
    "selected_lock_closure_digest",
    "selector",
    "selector_bootstrap_digest",
    "stdlib_digest",
    "uv_physical_sha256",
    "uv_version",
    "venv_bootstrap_digest",
    "wheel_declaration_digest",
)

FRAME_MAGIC: Final = b"W04CRSLT"
FRAME_VERSION: Final = 1
FRAME_HEADER_BYTES: Final = 14
FRAME_DIGEST_BYTES: Final = 32
MAX_FRAME_PAYLOAD_BYTES: Final = 16_777_216
MAX_DIAGNOSTIC_BYTES: Final = 1_048_576
CHILD_TIMEOUT_SECONDS: Final = 21_600.0

SCHEMA_BUNDLE_RELATIVE_PATH: Final = "configs/schema/wyscout-v5-schema-bundle-preimage-v2.json"
PRODUCT_CONTRACT_RELATIVE_PATH: Final = (
    "configs/schema/wyscout-v5-product-contract-preimage-v2.json"
)
SCHEMA_BUNDLE_V2_LOGICAL_SHA256: Final = (
    "956f5c3cedd9c9e2b36417ad87d8a9f2f97bc54b2720a6835a3cbcde668ff6e5"
)
PRODUCT_CONTRACT_V2_LOGICAL_SHA256: Final = (
    "fa2b28166df02663120f8cf9ca1751c0c32ff75a98b6255baf181bc179088f76"
)
PYPROJECT_SHA256: Final = "963db0004a52d36097bb66d7b5893044e7ac706580b14bae9e7e70e12ce5a89b"
UV_LOCK_SHA256: Final = "1c4d3408f3fd900443356f8387a1fed3554f9e0b69e74d9997cd99b60be134ca"
MANIFEST_SCHEMA_VERSION: Final = "w04-code-environment-admission-v16"
CHILD_RESULT_SCHEMA_VERSION: Final = "w04-child-result-v3"
FINAL_RECHECK_SCHEMA_VERSION: Final = "w04-rebuild-final-recheck-v2"
RUNTIME_SUBSET_ALGORITHM: Final = "w04-normalized-runtime-subset-observations-v1"
RUNTIME_SUBSET_POLICY: Final = "operational-R-subset-L-normalized-observation-v2"
RUNTIME_OBSERVATION_FIELDS: Final = (
    "observation_kind",
    "owner_name",
    "owner_version",
    "site_relative_path",
    "subject_name",
)
RUNTIME_OBSERVATION_KINDS: Final = (
    "MODULE_SOURCE",
    "NATIVE_EXTENSION",
    "NAMESPACE_LOCATION",
    "SITE_SHARED_IMAGE",
)
CHILD_PROCESS_OBSERVATION_FIELDS: Final = (
    "argv",
    "argv_sha256",
    "child_input_schema_version",
    "child_role",
    "cross_field_binding",
    "diagnostics_empty",
    "entrypoint_source",
    "exit_code",
    "final_uv_value",
    "frame_count",
    "frame_eof",
    "frame_magic",
    "frame_payload_sha256",
    "frame_payload_size_bytes",
    "frame_version",
    "in_place_pyc_unchanged",
    "initial_uv_value",
    "nonce",
    "not_timed_out",
    "payload_kind",
    "prefix_absolute_path",
    "prefix_empty_after",
    "prefix_empty_before",
    "prefix_identity_after",
    "prefix_identity_before",
    "prefix_identity_unchanged",
    "prefix_relative_path",
    "process_id",
    "result_descriptor_inheritable",
    "result_descriptor_number",
    "result_descriptor_parent_closed",
    "result_schema_version",
    "source_descriptor_checkpoint",
    "stderr_sha256",
    "stderr_size_bytes",
    "stdout_sha256",
    "stdout_size_bytes",
    "timeout_milliseconds",
    "transport_environment_sha256",
    "uv_path_resolution",
    "zero_in_place_pyc_reads",
)
ENTRYPOINT_OBSERVATION_FIELDS: Final = (
    "descriptor_cloexec",
    "descriptor_inheritable",
    "descriptor_number",
    "device",
    "inode",
    "link_count",
    "mode",
    "offset_after",
    "offset_before",
    "relative_path",
    "role",
    "sha256",
    "size_bytes",
    "source_eof",
)
CHILD_PROCESS_EXPECTED_FACT_FIELDS: Final = (
    "entrypoint_source",
    "frame_payload_sha256",
    "frame_payload_size_bytes",
    "nonce",
    "prefix_absolute_path",
    "prefix_identity_after",
    "prefix_identity_before",
    "prefix_relative_path",
    "process_id",
    "result_descriptor_number",
    "timeout_milliseconds",
    "transport_environment_sha256",
)
CHILD_INPUT_SCHEMA_VERSION: Final = "w04-child-input-v1"
SHA256_RE: Final = re.compile(r"^[0-9a-f]{64}$")
UUID4_RE: Final = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)

_OUTER_LITERAL_ENVIRONMENT: Final = {
    "ARROW_NUM_THREADS": "1",
    "LANG": "C",
    "LC_ALL": "C",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "POLARS_MAX_THREADS": "1",
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONHASHSEED": "0",
    "PYTHONIOENCODING": "utf-8:strict",
    "PYTHONNOUSERSITE": "1",
    "PYTHONUTF8": "1",
    "RAYON_NUM_THREADS": "1",
    "TZ": "UTC",
    "UV_LOCKED": "1",
    "UV_NO_SYNC": "1",
    "UV_OFFLINE": "1",
    "UV_RUN_RECURSION_DEPTH": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}
_OUTER_ENVIRONMENT_TOKENS: Final = {
    "HOME": "<W04_HOME>",
    "PATH": "<W04_VENV_BIN>:<W04_UV_BIN_DIR>:/usr/bin:/bin:/usr/sbin:/sbin",
    "PYTHONPYCACHEPREFIX": "<CONTROL_PREFIX>",
    "TMPDIR": "<W04_TMPDIR>",
    "UV": "<W04_UV_LOGICAL_LAUNCH_PATH>",
    "UV_CACHE_DIR": "<W04_UV_CACHE_ROOT>",
    "VIRTUAL_ENV": "<W04_PROJECT_ROOT>/.venv",
    "W04_LAUNCHER_SOURCE_FD": "<LAUNCHER_SOURCE_FD>",
    "__CF_USER_TEXT_ENCODING": "<W04_CF_USER_TEXT_ENCODING>",
}
OUTER_REQUIRED_ABSENT_ENVIRONMENT: Final = (
    "ALL_PROXY",
    "COVERAGE_PROCESS_CONFIG",
    "COVERAGE_PROCESS_START",
    "DYLD_FALLBACK_FRAMEWORK_PATH",
    "DYLD_FALLBACK_LIBRARY_PATH",
    "DYLD_FRAMEWORK_PATH",
    "DYLD_INSERT_LIBRARIES",
    "DYLD_LIBRARY_PATH",
    "HTTPS_PROXY",
    "HTTP_PROXY",
    "LD_LIBRARY_PATH",
    "LD_PRELOAD",
    "NO_PROXY",
    "PYTHONBREAKPOINT",
    "PYTHONHOME",
    "PYTHONINSPECT",
    "PYTHONOPTIMIZE",
    "PYTHONPATH",
    "PYTHONSTARTUP",
    "PYTHONUSERBASE",
    "PYTHONWARNINGS",
    "UV_DEFAULT_INDEX",
    "UV_EXTRA_INDEX_URL",
    "UV_FIND_LINKS",
    "UV_INDEX",
    "UV_PROJECT_ENVIRONMENT",
    "UV_PYTHON",
    "UV_PYTHON_PREFERENCE",
    "W04_BOOTSTRAP_TUPLE_B64",
    "W04_CHILD_INPUT_B64",
    "W04_CHILD_ROLE",
    "W04_ENTRYPOINT_SOURCE_FD",
    "W04_RESULT_FD",
    "W04_RESULT_NONCE",
    "all_proxy",
    "http_proxy",
    "https_proxy",
    "no_proxy",
)
OUTER_ENCODING_SOURCE_ROWS: Final = (
    {
        "module": "encodings",
        "path": "encodings/__init__.py",
        "sha256": "78c4744d407690f321565488710b5aaf6486b5afa8d185637aa1e7633ab59cd8",
        "size_bytes": 5_884,
    },
    {
        "module": "encodings.aliases",
        "path": "encodings/aliases.py",
        "sha256": "6fdcc49ba23a0203ae6cf28e608f8e6297d7c4d77d52e651db3cb49b9564c6d2",
        "size_bytes": 15_677,
    },
    {
        "module": "encodings.utf_8",
        "path": "encodings/utf_8.py",
        "sha256": "ba0cac060269583523ca9506473a755203037c57d466a11aa89a30a5f6756f3d",
        "size_bytes": 1_005,
    },
)

_REPOSITORY_CODE_PATHS: Final = (
    "scripts/__init__.py",
    "scripts/acquire_wyscout_v5.py",
    "scripts/admit_wyscout_v5_runtime.py",
    "scripts/apply_migrations.py",
    "scripts/control_utils.py",
    "scripts/install_local_git_guards.py",
    "scripts/launch_wyscout_v5.py",
    "scripts/materialize_wyscout_v5_contracts.py",
    "scripts/profile_wyscout_v5.py",
    "scripts/run_w03_protected_gate.py",
    "scripts/validate_w03_governance.py",
    "scripts/verify_local_only.py",
    "scripts/verify_parallel_safety.py",
    "scripts/verify_phase.py",
    "scripts/verify_task_return.py",
    "src/scouting/__init__.py",
    "src/scouting/audit/__init__.py",
    "src/scouting/audit/writer.py",
    "src/scouting/contracts/__init__.py",
    "src/scouting/contracts/audit.py",
    "src/scouting/contracts/evidence.py",
    "src/scouting/contracts/primitives.py",
    "src/scouting/contracts/retrieval.py",
    "src/scouting/contracts/workflow.py",
    "src/scouting/contracts/wyscout_aggregates.py",
    "src/scouting/contracts/wyscout_build.py",
    "src/scouting/contracts/wyscout_data.py",
    "src/scouting/contracts/wyscout_identity.py",
    "src/scouting/contracts/wyscout_schema.py",
    "src/scouting/identity/__init__.py",
    "src/scouting/identity/wyscout.py",
    "src/scouting/operations/__init__.py",
    "src/scouting/operations/telemetry.py",
    "src/scouting/policy/__init__.py",
    "src/scouting/policy/authentication.py",
    "src/scouting/policy/authorization.py",
    "src/scouting/policy/eligibility.py",
    "src/scouting/serving/__init__.py",
    "src/scouting/serving/synthetic.py",
    "src/scouting/sources/__init__.py",
    "src/scouting/sources/synthetic.py",
    "src/scouting/sources/wyscout.py",
    "src/scouting/sources/wyscout_completion_index.py",
    "src/scouting/sources/wyscout_manifest.py",
    "src/scouting/sources/wyscout_vertical_slice.py",
    "src/scouting/storage/__init__.py",
    "src/scouting/storage/embedded.py",
    "src/scouting/storage/formats.py",
    "src/scouting/storage/guarded.py",
    "src/scouting/storage/wyscout_publication.py",
    "src/scouting/web/__init__.py",
    "src/scouting/web/app.py",
    "src/scouting/workflow/__init__.py",
    "src/scouting/workflow/service.py",
)
_REPOSITORY_PYC_SOURCE_PATHS: Final = (
    "tests/contracts/test_foundation_contracts.py",
    "tests/contracts/test_w04_field_semantic_v2_authority.py",
    "tests/contracts/test_w04_identity_ruleset_authority.py",
    "tests/contracts/test_w04_logical_arrow_projection_authority.py",
    "tests/contracts/test_w04_possession_semantic_authority.py",
    "tests/contracts/test_w04_possession_semantic_v2_authority.py",
    "tests/contracts/test_w04_r21_control_preimages.py",
    "tests/contracts/test_w04_r21_cross_authority_composability.py",
    "tests/contracts/test_w04_source_temporal_review.py",
    "tests/contracts/test_w04_supported_feature_authority.py",
    "tests/contracts/test_w04_wyscout_build_contract.py",
    "tests/contracts/test_w04_wyscout_build_product_authority.py",
    "tests/contracts/test_w04_wyscout_identity_bundle.py",
    "tests/contracts/test_w04_wyscout_schema_closure.py",
    "tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py",
    "tests/contracts/test_w04_wyscout_v2_aggregates.py",
    "tests/contracts/test_wyscout_data_contracts.py",
    "tests/contracts/test_wyscout_field_registry_authority.py",
    "tests/e2e/test_w03_vertical_journey.py",
    "tests/e2e/test_w04_wyscout_vertical_slice.py",
    "tests/governance/test_w03_policies.py",
    "tests/governance/test_w04_source_authority.py",
    "tests/integration/test_migrations.py",
    "tests/integration/test_w03_local_telemetry.py",
    "tests/security/test_application_authorization.py",
    "tests/security/test_database_boundaries.py",
    "tests/security/test_w03_boundary_audit.py",
    "tests/security/test_w04_real_acquisition_review.py",
    "tests/security/test_w04_source_authority_boundary.py",
    "tests/security/test_w04_wyscout_ingest_review.py",
    "tests/security/test_w04_wyscout_profile_review.py",
    "tests/security/test_w04_wyscout_vertical_slice_publication.py",
    "tests/unit/test_foundation.py",
    "tests/unit/test_guarded_storage.py",
    "tests/unit/test_orchestration_controls.py",
    "tests/unit/test_synthetic_fixture.py",
    "tests/unit/test_w04_staged_product_publisher.py",
    "tests/unit/test_w04_wyscout_product_formats.py",
    "tests/unit/test_w04_wyscout_runtime_control.py",
    "tests/unit/test_w04_wyscout_vertical_slice_context.py",
    "tests/unit/test_wyscout_identity.py",
    "tests/unit/test_wyscout_profile.py",
    "tests/unit/test_wyscout_source.py",
    "tests/unit/test_wyscout_source_completion_index.py",
    "tests/unit/test_wyscout_source_manifest.py",
)

_POST_W04_RETIRED_AUDIT_ONLY_PYC_PREDICATES: Final = (
    {
        "authority_class": "REPOSITORY_RETIRED_POST_W04_CACHE_AUDIT_ONLY",
        "cache_path": (
            "tests/integration/__pycache__/"
            "test_w10_expert_relevance_evaluation.cpython-312-pytest-9.1.1.pyc"
        ),
        "denial_policy": "RETIRED_POST_W04_SOURCE_CACHE_DENIED_ZERO_READ",
        "source_path": "tests/integration/test_w10_expert_relevance_evaluation.py",
        "source_required_absent": True,
        "traversal_root_role": "WHOLE_REPOSITORY",
    },
)


def _derive_post_w04_audit_only_pyc_source_paths(
    root: Path,
    stable_repository_sources: frozenset[str],
) -> tuple[str, ...]:
    """Independently derive non-manifest Python sources using metadata only."""

    retired_sources = frozenset(
        cast(str, row["source_path"]) for row in _POST_W04_RETIRED_AUDIT_ONLY_PYC_PREDICATES
    )
    discovered: set[str] = set()
    for scope in ("scripts", "services", "src", "tests"):
        scope_root = root / scope
        if not scope_root.exists():
            continue
        for directory, directory_names, filenames in os.walk(scope_root, followlinks=False):
            retained_directories: list[str] = []
            for name in sorted(directory_names):
                if name == "__pycache__":
                    continue
                candidate = Path(directory) / name
                metadata = candidate.lstat()
                if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
                    raise RuntimeControlError(
                        "post-W04 Python source derivation encountered an unsafe directory"
                    )
                retained_directories.append(name)
            directory_names[:] = retained_directories
            for name in sorted(filenames):
                if not name.endswith(".py"):
                    continue
                candidate = Path(directory) / name
                metadata = candidate.lstat()
                if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
                    raise RuntimeControlError(
                        "post-W04 Python source derivation encountered an unsafe source"
                    )
                relative = candidate.relative_to(root).as_posix()
                if relative not in stable_repository_sources and relative not in retired_sources:
                    discovered.add(relative)
    return tuple(sorted(discovered))


_AUTHORIZED_DOWNSTREAM_CODE_PATHS: Final = (
    "scripts/rebuild_wyscout_v5.py",
    "src/scouting/data_products/wyscout/__init__.py",
    "src/scouting/data_products/wyscout/actions.py",
    "src/scouting/data_products/wyscout/bronze.py",
    "src/scouting/data_products/wyscout/gold.py",
    "src/scouting/data_products/wyscout/lineups.py",
    "src/scouting/data_products/wyscout/player_match.py",
    "src/scouting/data_products/wyscout/possessions.py",
    "src/scouting/data_products/wyscout/rebuild.py",
    "src/scouting/data_products/wyscout/silver_manifest.py",
    "src/scouting/data_products/wyscout/temporal_boundary.py",
)
_LOCAL_RESOURCE_DIGEST_ALGORITHM: Final = "w04-local-resource-exact-30-v1"
_LOCAL_RESOURCE_PATHS: Final = (
    "configs/schema/wyscout-v5-identity-ruleset-v1.yaml",
    "configs/schema/wyscout-v5-field-registry-v1.yaml",
    "configs/taxonomies/wyscout-v5-possession-taxonomy-v1.yaml",
    "configs/features/wyscout-v5-supported-count-features-v1.yaml",
    "reports/reviews/W04/authorities/wyscout-identity-ruleset-decisions-v1.json",
    "reports/reviews/W04/authorities/wyscout-identity-ruleset-independent-review-R1.md",
    "reports/reviews/W04/authorities/wyscout-identity-ruleset-acceptance-v1.json",
    "reports/reviews/W04/authorities/wyscout-field-semantic-decisions-v1.json",
    "reports/reviews/W04/authorities/wyscout-field-semantic-independent-review-R1.md",
    "reports/reviews/W04/authorities/wyscout-field-semantic-acceptance-v1.json",
    "reports/reviews/W04/authorities/wyscout-possession-semantic-decisions-v1.json",
    "reports/reviews/W04/authorities/wyscout-possession-semantic-independent-review-R1.md",
    "reports/reviews/W04/authorities/wyscout-possession-semantic-acceptance-v1.json",
    "reports/reviews/W04/authorities/wyscout-supported-feature-registry-decisions-v1.json",
    "reports/reviews/W04/authorities/wyscout-supported-feature-registry-independent-review-R1.md",
    "reports/reviews/W04/authorities/wyscout-supported-feature-registry-acceptance-v1.json",
    "reports/phase-gates/W04/source-schema-profile.md",
    "reports/reviews/W04/wyscout-schema-design-R21.md",
    "reports/reviews/W04/wyscout-schema-design-independent-review-R15.md",
    "configs/schema/wyscout-v5-product-contract-preimage-v1.json",
    "configs/schema/wyscout-v5-schema-bundle-preimage-v1.json",
    "reports/reviews/W04/authorities/wyscout-field-semantic-decisions-v2.json",
    "configs/schema/wyscout-v5-field-registry-v2.yaml",
    "reports/reviews/W04/authorities/wyscout-field-semantic-independent-review-v2-R1.md",
    "reports/reviews/W04/authorities/wyscout-field-semantic-acceptance-v2.json",
    "reports/reviews/W04/authorities/wyscout-possession-semantic-decisions-v2.json",
    "configs/taxonomies/wyscout-v5-possession-taxonomy-v2.yaml",
    "reports/reviews/W04/authorities/wyscout-possession-semantic-independent-review-v2-R1.md",
    "reports/reviews/W04/authorities/wyscout-possession-semantic-acceptance-v2.json",
    "tests/contracts/test_w04_r21_cross_authority_composability.py",
)

_STATIC_CHILD_ENVIRONMENT: Final = {
    "ARROW_NUM_THREADS": "1",
    "LANG": "C",
    "LC_ALL": "C",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "POLARS_MAX_THREADS": "1",
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONHASHSEED": "0",
    "PYTHONIOENCODING": "utf-8:strict",
    "PYTHONNOUSERSITE": "1",
    "PYTHONUTF8": "1",
    "RAYON_NUM_THREADS": "1",
    "TZ": "UTC",
    "UV_LOCKED": "1",
    "UV_NO_SYNC": "1",
    "UV_OFFLINE": "1",
    "UV_RUN_RECURSION_DEPTH": "0",
    "VECLIB_MAXIMUM_THREADS": "1",
}
_NORMALIZED_ENVIRONMENT_TOKENS: Final = {
    "HOME": "<W04_HOME>",
    "PATH": "<W04_VENV_BIN>:<W04_UV_BIN_DIR>:/usr/bin:/bin:/usr/sbin:/sbin",
    "PYTHONPYCACHEPREFIX": "<SELECTED_PREFIX>",
    "TMPDIR": "<W04_TMPDIR>",
    "UV": "<W04_UV_LOGICAL_LAUNCH_PATH>",
    "UV_CACHE_DIR": "<W04_UV_CACHE_ROOT>",
    "VIRTUAL_ENV": "<W04_PROJECT_ROOT>/.venv",
    "W04_ENTRYPOINT_SOURCE_FD": "<ENTRYPOINT_SOURCE_FD>",
    "W04_RESULT_FD": "<RESULT_FD>",
    "W04_RESULT_NONCE": "<RESULT_NONCE>",
    "__CF_USER_TEXT_ENCODING": "<W04_CF_USER_TEXT_ENCODING>",
}
REQUIRED_ABSENT_ENVIRONMENT: Final = (
    "ALL_PROXY",
    "COVERAGE_PROCESS_CONFIG",
    "COVERAGE_PROCESS_START",
    "DYLD_FALLBACK_FRAMEWORK_PATH",
    "DYLD_FALLBACK_LIBRARY_PATH",
    "DYLD_FRAMEWORK_PATH",
    "DYLD_INSERT_LIBRARIES",
    "DYLD_LIBRARY_PATH",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "LD_LIBRARY_PATH",
    "LD_PRELOAD",
    "NO_PROXY",
    "PYTHONBREAKPOINT",
    "PYTHONHOME",
    "PYTHONINSPECT",
    "PYTHONOPTIMIZE",
    "PYTHONPATH",
    "PYTHONSTARTUP",
    "PYTHONUSERBASE",
    "PYTHONWARNINGS",
    "UV_DEFAULT_INDEX",
    "UV_EXTRA_INDEX_URL",
    "UV_FIND_LINKS",
    "UV_INDEX",
    "UV_PROJECT_ENVIRONMENT",
    "UV_PYTHON",
    "UV_PYTHON_PREFERENCE",
    "W04_BOOTSTRAP_TUPLE_B64",
    "W04_LAUNCHER_SOURCE_FD",
    "all_proxy",
    "http_proxy",
    "https_proxy",
    "no_proxy",
)


class RuntimeControlError(RuntimeError):
    """A closed W04 runtime-control predicate failed."""


class ChildProcessError(RuntimeControlError):
    """A bounded admission or rebuild child failed."""


class ResultFrameError(RuntimeControlError):
    """A child result frame is malformed, truncated, or non-canonical."""


@dataclass(frozen=True, slots=True)
class RuntimeControlRoots:
    """Caller-supplied isolated exact roots used by the accepted publisher."""

    manifest_final_root: Path
    manifest_staging_root: Path
    pycache_staging_root: Path


@dataclass(frozen=True, slots=True)
class ChildProcessEvidence:
    """Immutable canonical observation plus separately captured retained facts."""

    expected_facts_bytes: bytes
    observation_bytes: bytes
    payload_bytes: bytes
    role: str

    def validate(self, envelope: object | None = None) -> dict[str, object]:
        expected_value = _load_canonical_json(self.expected_facts_bytes)
        payload_value = _load_canonical_json(self.payload_bytes)
        if type(expected_value) is not dict or type(payload_value) is not dict:
            raise RuntimeControlError("child process retained evidence is not object-shaped")
        if (
            _canonical_json_bytes(expected_value) != self.expected_facts_bytes
            or _canonical_json_bytes(payload_value) != self.payload_bytes
        ):
            raise RuntimeControlError("child process retained evidence is not canonical")
        expected_facts = cast(dict[str, object], expected_value)
        payload = cast(dict[str, object], payload_value)
        if tuple(expected_facts) != CHILD_PROCESS_EXPECTED_FACT_FIELDS:
            raise RuntimeControlError("child process retained fact roster/order differs")
        observation = _decode_child_process_observation(
            self.observation_bytes,
            expected_role=self.role,
            expected_facts=expected_facts,
        )
        if (
            payload.get("child_role") != self.role
            or payload.get("schema_version") != CHILD_RESULT_SCHEMA_VERSION
            or payload.get("nonce") != observation["nonce"]
            or payload.get("payload_kind") != observation["payload_kind"]
            or payload.get("child_environment_sha256")
            != observation["transport_environment_sha256"]
            or payload.get("entrypoint_source") != observation["entrypoint_source"]
            or _sha256(self.payload_bytes) != observation["frame_payload_sha256"]
            or len(self.payload_bytes) != observation["frame_payload_size_bytes"]
        ):
            raise RuntimeControlError("child process payload/observation cross-binding differs")
        if envelope is not None:
            model_dump = getattr(envelope, "model_dump", None)
            if (
                model_dump is None
                or _canonical_json_bytes(model_dump(mode="json")) != self.payload_bytes
            ):
                raise RuntimeControlError("current child envelope differs from retained payload")
        return observation


@dataclass(frozen=True, slots=True)
class WyscoutLaunchPlan:
    """Frozen post-hash plan; creating it does not execute the rebuild."""

    build_id: str
    run_id: str
    code_manifest_id: str
    code_manifest_sha256: str
    code_manifest_relative_path: str
    layer_manifest_relative_paths: tuple[str, str, str]
    rebuild_prefix_relative_path: str
    rebuild_receipt_relative_path: str
    rebuild_argv: tuple[str, ...]
    invocation: "RebuildInvocation"
    admission_process_evidence: ChildProcessEvidence


@dataclass(frozen=True, slots=True)
class ChildExecution:
    """Validated child result plus bounded diagnostic receipts."""

    envelope: "ChildResultEnvelope"
    stdout: bytes
    stderr: bytes
    process_evidence: ChildProcessEvidence


@dataclass(frozen=True, slots=True)
class _GuardedSource:
    descriptor: int
    relative_path: str
    sha256: str
    size_bytes: int
    device: int
    inode: int


def _install_runtime_import_roots(project_root: Path) -> None:
    roots = (
        project_root / "src",
        project_root / ".venv" / "lib" / "python3.12" / "site-packages",
    )
    for root in reversed(roots):
        spelling = os.fspath(root)
        if spelling not in sys.path:
            sys.path.insert(0, spelling)


def _runtime_contracts(project_root: Path) -> tuple[ModuleType, ModuleType]:
    _install_runtime_import_roots(project_root)
    from scouting.contracts import wyscout_build
    from scouting.storage import wyscout_publication

    return wyscout_build, wyscout_publication


def _canonical_json_bytes(value: object) -> bytes:
    if isinstance(value, dict):
        value = {key: value[key] for key in sorted(value)}
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise RuntimeControlError("value is not canonical-JSON encodable") from error


def _load_canonical_json(raw: bytes) -> object:
    if not raw or raw.endswith(b"\n"):
        raise RuntimeControlError("canonical JSON transport must be nonempty and have no LF")

    def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise RuntimeControlError(f"duplicate canonical JSON key: {key}")
            result[key] = value
        return result

    try:
        value = json.loads(
            raw.decode("utf-8", errors="strict"), object_pairs_hook=reject_duplicates
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuntimeControlError("invalid canonical JSON transport") from error
    if _canonical_json_bytes(value) != raw:
        raise RuntimeControlError("JSON transport is not byte-canonical")
    return value


def _load_strict_json(raw: bytes) -> object:
    def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise RuntimeControlError(f"duplicate strict JSON key: {key}")
            result[key] = value
        return result

    try:
        return json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=reject_duplicates)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuntimeControlError("invalid strict JSON") from error


def decode_result_frame(frame: bytes) -> bytes:
    """Validate the one exhaustive W04 child-result frame and return its payload."""

    if not isinstance(frame, bytes) or len(frame) < FRAME_HEADER_BYTES + FRAME_DIGEST_BYTES:
        raise ResultFrameError("child result frame is truncated")
    if frame[:8] != FRAME_MAGIC:
        raise ResultFrameError("child result frame magic differs")
    if int.from_bytes(frame[8:10], "big") != FRAME_VERSION:
        raise ResultFrameError("child result frame version differs")
    length = int.from_bytes(frame[10:14], "big")
    if not 1 <= length <= MAX_FRAME_PAYLOAD_BYTES:
        raise ResultFrameError("child result payload length is outside the bound")
    expected_size = FRAME_HEADER_BYTES + length + FRAME_DIGEST_BYTES
    if len(frame) != expected_size:
        raise ResultFrameError("child result frame has truncation or trailing bytes")
    payload = frame[FRAME_HEADER_BYTES : FRAME_HEADER_BYTES + length]
    if hashlib.sha256(payload).digest() != frame[-FRAME_DIGEST_BYTES:]:
        raise ResultFrameError("child result payload digest differs")
    try:
        decoded = _load_canonical_json(payload)
    except RuntimeControlError as error:
        raise ResultFrameError("child result payload is not canonical JSON") from error
    if type(decoded) is not dict:
        raise ResultFrameError("child result payload must be an object")
    return payload


def _safe_uuid4(value: str, *, label: str) -> str:
    if not isinstance(value, str) or UUID4_RE.fullmatch(value) is None:
        raise RuntimeControlError(f"{label} must be a canonical UUIDv4")
    if str(UUID(value)) != value:
        raise RuntimeControlError(f"{label} is not canonical")
    return value


def _sample_distinct_uuid4(*, excluded: set[str], label: str) -> str:
    for _attempt in range(16):
        candidate = _safe_uuid4(str(uuid4()), label=label)
        if candidate not in excluded:
            return candidate
    raise RuntimeControlError(f"{label} could not sample a distinct UUIDv4")


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _outer_environment_authority() -> dict[str, object]:
    present = {**_OUTER_LITERAL_ENVIRONMENT, **_OUTER_ENVIRONMENT_TOKENS}
    return {
        "algorithm": "w04-outer-environment-bootstrap-v2",
        "excluded_until_insertion": ["W04_BOOTSTRAP_TUPLE_B64"],
        "present": {key: present[key] for key in sorted(present)},
        "required_absent": list(OUTER_REQUIRED_ABSENT_ENVIRONMENT),
    }


def _outer_bootstrap_tuple(
    *, project_root: Path, launcher_sha256: str, launcher_size: int
) -> dict[str, object]:
    if (
        SHA256_RE.fullmatch(launcher_sha256) is None
        or type(launcher_size) is not int
        or launcher_size <= 0
    ):
        raise RuntimeControlError("outer launcher byte authority is malformed")
    return {
        "control_prefix_policy": "w04-three-role-runtime-pycache-v1",
        "control_prefix_relative_template": (
            "data/working/wyscout/v5/.staging/control/control_run_id=<uuid>/runtime-pycache/"
        ),
        "encoding_source_rows": [dict(row) for row in OUTER_ENCODING_SOURCE_ROWS],
        "fixed_environment_algorithm": "w04-outer-environment-bootstrap-v2",
        "fixed_environment_digest": _sha256(_canonical_json_bytes(_outer_environment_authority())),
        "launcher_mode": 0o644,
        "launcher_relative_path": "scripts/launch_wyscout_v5.py",
        "launcher_sha256": launcher_sha256,
        "launcher_size": launcher_size,
        "launcher_source_descriptor_policy": "w04-inherited-source-fd-v1",
        "ordered_argv": list(OUTER_ARGV),
        "process_role": "W04_LOCAL_CONTROL",
        "pyproject_sha256": PYPROJECT_SHA256,
        "python_physical_mode": 0o755,
        "python_physical_sha256": (
            "cf450e6bc0b00adecd12b7b13024de7000c7350801addc802bd3b45782104e79"
        ),
        "python_physical_size": 49_968,
        "python_version": "3.12.12",
        "uv_host_spelling_normalization": "w04-uv-host-spelling-normalization-v1",
        "uv_final_entry_kind": "regular_non_symlink_executable",
        "uv_installation_root_role": "<W04_UV_INSTALLATION_ROOT>",
        "uv_link_policy": "w04-uv-logical-one-hop-relative-link-v1",
        "uv_logical_entry_kind": "symlink",
        "uv_logical_launch_role": "<W04_UV_LOGICAL_LAUNCH>",
        "uv_physical_executable_role": "<W04_UV_PHYSICAL_EXECUTABLE>",
        "uv_physical_mode": 0o555,
        "uv_physical_sha256": ("4f0c0c002bb4702c1bd6792edc15f7ae3948b5f19509c8d73cd5c9a26298097f"),
        "uv_physical_size": 41_617_552,
        "uv_raw_target_form": "relative_nonempty_nul_free_posix",
        "uv_raw_target_must_not_be_absolute": True,
        "uv_resolution_containment": "W04_UV_INSTALLATION_ROOT",
        "uv_resolution_hops": 1,
        "uv_version": "uv 0.9.21 (Homebrew 2025-12-30)",
        "uv_lock_sha256": UV_LOCK_SHA256,
        "working_directory": "<W04_PROJECT_ROOT>",
    }


def outer_bootstrap_transport(
    *, project_root: Path, control_prefix: Path, launcher_source_fd: int
) -> tuple[dict[str, str], dict[str, object]]:
    """Construct the exact master-owned pre-uv transport for verification."""

    root = project_root.absolute()
    prefix = control_prefix.absolute()
    if (
        type(launcher_source_fd) is not int
        or launcher_source_fd < 3
        or launcher_source_fd > 2_147_483_647
    ):
        raise RuntimeControlError("outer launcher source descriptor is malformed")
    descriptor_metadata = os.fstat(launcher_source_fd)
    path_metadata = os.stat(root / "scripts/launch_wyscout_v5.py", follow_symlinks=False)
    if (
        not stat.S_ISREG(descriptor_metadata.st_mode)
        or stat.S_IMODE(descriptor_metadata.st_mode) != 0o644
        or descriptor_metadata.st_nlink != 1
        or (
            descriptor_metadata.st_dev,
            descriptor_metadata.st_ino,
            descriptor_metadata.st_mode,
            descriptor_metadata.st_nlink,
            descriptor_metadata.st_size,
        )
        != (
            path_metadata.st_dev,
            path_metadata.st_ino,
            path_metadata.st_mode,
            path_metadata.st_nlink,
            path_metadata.st_size,
        )
        or os.lseek(launcher_source_fd, 0, os.SEEK_CUR) != 0
    ):
        raise RuntimeControlError("master-opened launcher descriptor authority differs")
    launcher_raw = b"".join(
        os.pread(
            launcher_source_fd,
            min(1024 * 1024, descriptor_metadata.st_size - offset),
            offset,
        )
        for offset in range(0, descriptor_metadata.st_size, 1024 * 1024)
    )
    if (
        len(launcher_raw) != descriptor_metadata.st_size
        or os.pread(launcher_source_fd, 1, descriptor_metadata.st_size) != b""
        or os.lseek(launcher_source_fd, 0, os.SEEK_CUR) != 0
    ):
        raise RuntimeControlError("master-opened launcher descriptor bytes differ")
    bootstrap = _outer_bootstrap_tuple(
        project_root=root,
        launcher_sha256=_sha256(launcher_raw),
        launcher_size=len(launcher_raw),
    )
    encoded = base64.urlsafe_b64encode(_canonical_json_bytes(bootstrap)).decode().rstrip("=")
    environment = {
        **_OUTER_LITERAL_ENVIRONMENT,
        "HOME": "/Users/adrian",
        "PATH": "/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        "PYTHONPYCACHEPREFIX": os.fspath(prefix),
        "TMPDIR": "/var/folders/8r/chc2bb390r9cw7s2m65b21h80000gn/T/",
        "UV": "/opt/homebrew/bin/uv",
        "UV_CACHE_DIR": "/Users/adrian/.cache/uv",
        "VIRTUAL_ENV": os.fspath(root / ".venv"),
        "W04_BOOTSTRAP_TUPLE_B64": encoded,
        "W04_LAUNCHER_SOURCE_FD": str(launcher_source_fd),
        "__CF_USER_TEXT_ENCODING": "0x1F5:0:2",
    }
    environment["UV_RUN_RECURSION_DEPTH"] = "0"
    return environment, bootstrap


def _guard_read_relative(
    project_root: Path,
    relative_path: str,
    *,
    expected_mode: int = 0o644,
    max_bytes: int = 64 * 1024 * 1024,
) -> bytes:
    """No-follow read one explicit project-relative regular file."""

    if (
        not relative_path
        or relative_path.startswith("/")
        or relative_path.endswith("/")
        or "\\" in relative_path
        or any(part in {"", ".", ".."} for part in relative_path.split("/"))
    ):
        raise RuntimeControlError("unsafe explicit repository-relative path")
    root_fd = os.open(project_root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    descriptors = [root_fd]
    try:
        current = root_fd
        parts = relative_path.split("/")
        for part in parts[:-1]:
            before = os.stat(part, dir_fd=current, follow_symlinks=False)
            if not stat.S_ISDIR(before.st_mode) or stat.S_ISLNK(before.st_mode):
                raise RuntimeControlError("guard path crosses a link or non-directory")
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=current)
            after = os.fstat(child)
            if (before.st_dev, before.st_ino, before.st_mode) != (
                after.st_dev,
                after.st_ino,
                after.st_mode,
            ):
                os.close(child)
                raise RuntimeControlError("guard directory changed during open")
            descriptors.append(child)
            current = child
        before = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        if (
            not stat.S_ISREG(before.st_mode)
            or stat.S_ISLNK(before.st_mode)
            or stat.S_IMODE(before.st_mode) != expected_mode
            or before.st_nlink != 1
            or not 1 <= before.st_size <= max_bytes
        ):
            raise RuntimeControlError("guarded file kind, mode, link count, or size differs")
        file_fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=current)
        try:
            opened = os.fstat(file_fd)
            if (before.st_dev, before.st_ino, before.st_mode, before.st_nlink, before.st_size) != (
                opened.st_dev,
                opened.st_ino,
                opened.st_mode,
                opened.st_nlink,
                opened.st_size,
            ):
                raise RuntimeControlError("guarded file changed during open")
            chunks: list[bytes] = []
            remaining = opened.st_size
            while remaining:
                chunk = os.read(file_fd, min(remaining, 1024 * 1024))
                if not chunk:
                    raise RuntimeControlError("guarded file ended early")
                chunks.append(chunk)
                remaining -= len(chunk)
            if os.read(file_fd, 1) != b"":
                raise RuntimeControlError("guarded file grew during read")
            after = os.fstat(file_fd)
            if (opened.st_dev, opened.st_ino, opened.st_mode, opened.st_nlink, opened.st_size) != (
                after.st_dev,
                after.st_ino,
                after.st_mode,
                after.st_nlink,
                after.st_size,
            ):
                raise RuntimeControlError("guarded file changed during read")
            return b"".join(chunks)
        finally:
            os.close(file_fd)
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def _guard_v2_aggregates(project_root: Path) -> tuple[str, str]:
    schema_raw = _guard_read_relative(project_root, SCHEMA_BUNDLE_RELATIVE_PATH)
    product_raw = _guard_read_relative(project_root, PRODUCT_CONTRACT_RELATIVE_PATH)
    for label, raw, expected in (
        ("schema bundle", schema_raw, SCHEMA_BUNDLE_V2_LOGICAL_SHA256),
        ("product contract", product_raw, PRODUCT_CONTRACT_V2_LOGICAL_SHA256),
    ):
        if not raw.endswith(b"\n") or raw[:-1].endswith(b"\n"):
            raise RuntimeControlError(f"{label} must have exactly one physical terminal LF")
        _load_canonical_json(raw[:-1])
        if _sha256(raw[:-1]) != expected:
            raise RuntimeControlError(f"{label} logical v2 digest differs")
    return SCHEMA_BUNDLE_V2_LOGICAL_SHA256, PRODUCT_CONTRACT_V2_LOGICAL_SHA256


def _sha256_json(value: object) -> str:
    return _sha256(_canonical_json_bytes(value))


def _authority_file_row(root: Path, relative: str, *, mode: int = 0o644) -> dict[str, object]:
    raw = _guard_read_relative(root, relative, expected_mode=mode, max_bytes=128 * 1024 * 1024)
    return {"mode": mode, "path": relative, "sha256": _sha256(raw), "size_bytes": len(raw)}


def _independent_repository_rows(root: Path) -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = [
        _authority_file_row(root, path)
        for path in (*_REPOSITORY_CODE_PATHS, *_REPOSITORY_PYC_SOURCE_PATHS)
    ]
    for relative in _AUTHORIZED_DOWNSTREAM_CODE_PATHS:
        candidate = root / relative
        if not candidate.exists():
            rows.append({"path": relative, "state": "AUTHORIZED_ABSENT"})
        else:
            row = _authority_file_row(root, relative)
            row["state"] = "PRESENT"
            rows.append(row)
    return tuple(rows)


def _absolute_regular(path: Path, *, mode: int | None = None) -> bytes:
    before = os.stat(path, follow_symlinks=False)
    if (
        not stat.S_ISREG(before.st_mode)
        or stat.S_ISLNK(before.st_mode)
        or before.st_nlink != 1
        or (mode is not None and stat.S_IMODE(before.st_mode) != mode)
    ):
        raise RuntimeControlError("retained authority target is not a singular regular file")
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        opened = os.fstat(descriptor)
        raw = b""
        chunks: list[bytes] = []
        while chunk := os.read(descriptor, 1024 * 1024):
            chunks.append(chunk)
        raw = b"".join(chunks)
        after = os.fstat(descriptor)
        if (
            (before.st_dev, before.st_ino, before.st_mode, before.st_size)
            != (opened.st_dev, opened.st_ino, opened.st_mode, opened.st_size)
            or (opened.st_dev, opened.st_ino, opened.st_mode, opened.st_size)
            != (after.st_dev, after.st_ino, after.st_mode, after.st_size)
            or len(raw) != after.st_size
        ):
            raise RuntimeControlError("retained authority target changed during read")
        return raw
    finally:
        os.close(descriptor)


def _independent_lock_rows(root: Path) -> tuple[dict[str, object], ...]:
    lock_raw = _guard_read_relative(root, "uv.lock", max_bytes=128 * 1024 * 1024)
    parsed = tomllib.loads(lock_raw.decode("utf-8", errors="strict"))
    packages = parsed.get("package")
    if type(packages) is not list or len(packages) != 83:
        raise RuntimeControlError("retained lock package roster differs")
    rows = tuple(
        {
            "name": package["name"],
            "source": package.get("source"),
            "version": package["version"],
        }
        for package in packages
        if package["name"] not in {"colorama", "scouting-intelligence"}
    )
    if len(rows) != 81:
        raise RuntimeControlError("retained selected lock cardinality differs")
    return rows


def _independent_installed_rows(
    root: Path, closure: tuple[dict[str, object], ...]
) -> tuple[dict[str, object], ...]:
    site = root / ".venv/lib/python3.12/site-packages"
    installed: dict[str, tuple[str, Path]] = {}
    for entry in os.scandir(site):
        if not entry.name.endswith(".dist-info"):
            continue
        metadata = entry.stat(follow_symlinks=False)
        if not stat.S_ISDIR(metadata.st_mode) or entry.is_symlink():
            raise RuntimeControlError("retained dist-info census contains an unsafe entry")
        raw = _absolute_regular(Path(entry.path) / "METADATA", mode=0o644)
        headers = raw.decode("utf-8", errors="strict").split("\n\n", 1)[0].splitlines()
        names = [line[6:] for line in headers if line.startswith("Name: ")]
        versions = [line[9:] for line in headers if line.startswith("Version: ")]
        if len(names) != 1 or len(versions) != 1:
            raise RuntimeControlError("retained METADATA identity is not singular")
        normalized = re.sub(r"[-_.]+", "-", names[0]).lower()
        expected_dist_info = f"{normalized.replace('-', '_')}-{versions[0]}.dist-info"
        if entry.name != expected_dist_info:
            raise RuntimeControlError("retained dist-info name/version association differs")
        if normalized in installed:
            raise RuntimeControlError("retained installed identity is duplicated")
        installed[normalized] = (versions[0], Path(entry.path))
    expected = {cast(str, row["name"]): cast(str, row["version"]) for row in closure}
    expected["scouting-intelligence"] = "0.1.0"
    if {name: value[0] for name, value in installed.items()} != expected:
        raise RuntimeControlError("retained L==I distribution equality differs")
    packages: list[dict[str, object]] = []
    for locked in closure:
        name, version = cast(str, locked["name"]), cast(str, locked["version"])
        dist_info = installed[name][1]
        declarations = list(
            csv.reader(_absolute_regular(dist_info / "RECORD", mode=0o644).decode().splitlines())
        )
        self_path = f"{dist_info.name}/RECORD"
        seen: set[str] = set()
        records: list[dict[str, object]] = []
        if not declarations or any(len(row) != 3 for row in declarations):
            raise RuntimeControlError("retained installed RECORD row shape differs")
        for relative, digest_cell, size_cell in declarations:
            parts = tuple(relative.split("/"))
            executable_scheme = (
                len(parts) == 5
                and parts[:4] == ("..", "..", "..", "bin")
                and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", parts[4]) is not None
            )
            mapped_external_candidate = ".." in parts and not executable_scheme
            if (
                Path(relative).is_absolute()
                or "\\" in relative
                or any(part in {"", "."} for part in parts)
                or (not executable_scheme and not mapped_external_candidate and ".." in parts)
                or relative in seen
                or relative.lower().endswith((".pyc", ".pyo"))
            ):
                raise RuntimeControlError("retained RECORD is duplicated or grants bytecode")
            seen.add(relative)
            if relative == self_path:
                if digest_cell or size_cell:
                    raise RuntimeControlError("retained RECORD self row differs")
                records.append({"path": relative, "self": True})
                continue
            target = Path(os.path.normpath(os.fspath(site / relative)))
            if not target.is_relative_to(root / ".venv"):
                raise RuntimeControlError("retained RECORD target escapes venv")
            metadata = os.stat(target, follow_symlinks=False)
            raw = _absolute_regular(target, mode=stat.S_IMODE(metadata.st_mode))
            encoded = base64.urlsafe_b64encode(hashlib.sha256(raw).digest()).decode().rstrip("=")
            if digest_cell != f"sha256={encoded}" or size_cell != str(len(raw)):
                raise RuntimeControlError("retained RECORD target declaration differs")
            records.append(
                {
                    "mode": stat.S_IMODE(metadata.st_mode),
                    "path": relative,
                    "sha256": _sha256(raw),
                    "size_bytes": len(raw),
                }
            )
        installer = next(row for row in records if row.get("path") == f"{dist_info.name}/INSTALLER")
        requested = next(row for row in records if row.get("path") == f"{dist_info.name}/REQUESTED")
        if installer["sha256"] != _sha256(b"uv") or requested["size_bytes"] != 0:
            raise RuntimeControlError("retained generated installer rows differ")
        packages.append({"name": name, "record_rows": records, "version": version})
    return tuple(packages)


def _independent_require_site_ancestry(site: Path, target: Path, *, include_leaf: bool) -> None:
    if not target.is_relative_to(site):
        raise RuntimeControlError("runtime path escapes frozen site authority")
    site_metadata = os.stat(site, follow_symlinks=False)
    if not stat.S_ISDIR(site_metadata.st_mode) or stat.S_ISLNK(site_metadata.st_mode):
        raise RuntimeControlError("runtime frozen site root is unsafe")
    relative = target.relative_to(site)
    parts = relative.parts if include_leaf else relative.parts[:-1]
    current = site
    for part in parts:
        current = current / part
        metadata = os.stat(current, follow_symlinks=False)
        if not stat.S_ISDIR(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
            raise RuntimeControlError("runtime path has an unsafe site parent")


@dataclass(frozen=True, slots=True)
class _IndependentRuntimeSubsetAuthority:
    """Pre-child selected/RECORD authority for independent returned-R validation."""

    extension_suffixes: tuple[str, ...]
    owners: dict[str, tuple[str, str, int, int, str]]
    project_root: Path
    selected_owners: frozenset[tuple[str, str]]
    site: Path

    def validate(self, final_recheck: object) -> None:
        digest = getattr(final_recheck, "runtime_subset_digest", None)
        model_rows = getattr(final_recheck, "runtime_subset_rows", None)
        if type(digest) is not str or type(model_rows) is not tuple:
            raise RuntimeControlError("rebuild final recheck lacks normalized runtime subset")
        rows = tuple(row.model_dump(mode="json") for row in model_rows)
        if not 1 <= len(rows) <= 100_000:
            raise RuntimeControlError("runtime subset row cardinality differs")
        row_bytes: list[bytes] = []
        observed_owners: set[tuple[str, str]] = set()
        native_owners: dict[str, tuple[str, str]] = {}
        observed_owner_by_root: dict[str, set[tuple[str, str]]] = {}
        for row in rows:
            if tuple(row) != RUNTIME_OBSERVATION_FIELDS:
                raise RuntimeControlError("runtime subset row roster/order differs")
            if any(type(row[field]) is not str for field in RUNTIME_OBSERVATION_FIELDS):
                raise RuntimeControlError("runtime subset row contains a mistyped value")
            if any(not is_normalized("NFC", cast(str, row[field])) for field in row):
                raise RuntimeControlError("runtime subset row is not NFC")
            kind = cast(str, row["observation_kind"])
            owner_name = cast(str, row["owner_name"])
            owner_version = cast(str, row["owner_version"])
            relative = cast(str, row["site_relative_path"])
            subject = cast(str, row["subject_name"])
            if kind not in RUNTIME_OBSERVATION_KINDS:
                raise RuntimeControlError("runtime subset observation kind differs")
            if (
                Path(relative).is_absolute()
                or "\\" in relative
                or relative.endswith("/")
                or any(part in {"", ".", ".."} for part in relative.split("/"))
                or relative.lower().endswith((".pyc", ".pyo"))
            ):
                raise RuntimeControlError("runtime subset site path is unsafe")
            owner_identity = (owner_name, owner_version)
            if owner_identity not in self.selected_owners:
                raise RuntimeControlError("runtime subset owner is outside frozen selected L")
            observed_owners.add(owner_identity)
            if kind == "NAMESPACE_LOCATION":
                observed_owner_by_root.setdefault(subject.split(".", 1)[0], set()).add(
                    owner_identity
                )
                namespace = self.site / relative
                _independent_require_site_ancestry(self.site, namespace, include_leaf=True)
                metadata = os.stat(namespace, follow_symlinks=False)
                if not stat.S_ISDIR(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
                    raise RuntimeControlError("runtime namespace location is unsafe")
                prefix = relative + "/"
                if prefix + "__init__.py" in self.owners:
                    raise RuntimeControlError("runtime namespace has an owned initializer")
                descendants = {
                    value[:2]
                    for path, value in self.owners.items()
                    if path.startswith(prefix) and "/__pycache__/" not in path
                }
                if owner_identity not in descendants:
                    raise RuntimeControlError("runtime namespace owner lacks a frozen descendant")
                if subject != relative.replace("/", "."):
                    raise RuntimeControlError("runtime namespace subject/location differs")
            else:
                frozen = self.owners.get(relative)
                if frozen is None or frozen[:2] != owner_identity:
                    raise RuntimeControlError("runtime concrete row owner/path differs")
                mode, size, expected_digest = frozen[2:]
                _independent_require_site_ancestry(
                    self.site, self.site / relative, include_leaf=False
                )
                raw = _absolute_regular(self.site / relative, mode=mode)
                if len(raw) != size or _sha256(raw) != expected_digest:
                    raise RuntimeControlError("runtime concrete row bytes differ")
                if kind == "MODULE_SOURCE" and not relative.endswith(".py"):
                    raise RuntimeControlError("runtime source row does not identify source")
                if kind == "MODULE_SOURCE":
                    observed_owner_by_root.setdefault(subject.split(".", 1)[0], set()).add(
                        owner_identity
                    )
                    expected_subject = (
                        relative[: -len("/__init__.py")].replace("/", ".")
                        if relative.endswith("/__init__.py")
                        else relative[:-3].replace("/", ".")
                    )
                    if subject != expected_subject:
                        raise RuntimeControlError("runtime source subject/path differs")
                if kind == "NATIVE_EXTENSION":
                    observed_owner_by_root.setdefault(subject.split(".", 1)[0], set()).add(
                        owner_identity
                    )
                    if not any(relative.endswith(suffix) for suffix in self.extension_suffixes):
                        raise RuntimeControlError("runtime native row suffix differs")
                    suffix = next(
                        suffix for suffix in self.extension_suffixes if relative.endswith(suffix)
                    )
                    if subject != relative[: -len(suffix)].replace("/", "."):
                        raise RuntimeControlError("runtime native subject/path differs")
                    module_root = subject.split(".", 1)[0]
                    existing_native_owner = native_owners.get(module_root)
                    if (
                        existing_native_owner is not None
                        and existing_native_owner != owner_identity
                    ):
                        raise RuntimeControlError("runtime native top-level owner is ambiguous")
                    native_owners[module_root] = owner_identity
                if kind == "SITE_SHARED_IMAGE" and subject != "DYLD_IMAGE":
                    raise RuntimeControlError("runtime shared-image subject differs")
                if kind == "SITE_SHARED_IMAGE":
                    observed_owner_by_root.setdefault(relative.split("/", 1)[0], set()).add(
                        owner_identity
                    )
                if (
                    kind == "SITE_SHARED_IMAGE"
                    and not relative.endswith((".so", ".dylib"))
                    and not any(relative.endswith(suffix) for suffix in self.extension_suffixes)
                ):
                    raise RuntimeControlError("runtime shared-image suffix differs")
            row_bytes.append(_canonical_json_bytes(row))
        if row_bytes != sorted(row_bytes) or len(set(row_bytes)) != len(row_bytes):
            raise RuntimeControlError("runtime subset rows are not uniquely byte sorted")
        if not observed_owners or not observed_owners.issubset(self.selected_owners):
            raise RuntimeControlError("runtime subset is not nonempty R subset L")
        if digest != _sha256_json({"algorithm": RUNTIME_SUBSET_ALGORITHM, "rows": rows}):
            raise RuntimeControlError("runtime subset digest differs from exact rows")
        for subject, owner in (
            ("pydantic_core", "pydantic-core"),
            ("_polars_runtime_32", "polars-runtime-32"),
        ):
            observed_root_owners = observed_owner_by_root.get(subject, set())
            native_owner = native_owners.get(subject)
            if observed_root_owners and (
                native_owner is None
                or native_owner[0] != owner
                or observed_root_owners != {native_owner}
            ):
                raise RuntimeControlError(f"runtime native owner mapping differs: {subject}")


def _freeze_independent_runtime_subset_authority(
    project_root: Path,
) -> _IndependentRuntimeSubsetAuthority:
    """Freeze independent L and complete RECORD ownership exactly once pre-child."""

    preliminary = _independent_lock_rows(project_root)
    installed = _independent_installed_rows(project_root, preliminary)
    _selector, selected, _wheels = _independent_selector_closure_wheels(
        project_root, preliminary, installed
    )
    selected_owners = frozenset(
        (cast(str, row["name"]), cast(str, row["version"])) for row in selected
    )
    site = project_root / ".venv/lib/python3.12/site-packages"
    owners: dict[str, tuple[str, str, int, int, str]] = {}
    for package in installed:
        identity = (cast(str, package["name"]), cast(str, package["version"]))
        if identity not in selected_owners:
            continue
        for row in cast(list[dict[str, object]], package["record_rows"]):
            if row.get("self") is True or "sha256" not in row:
                continue
            target = Path(os.path.normpath(os.fspath(site / cast(str, row["path"]))))
            if not target.is_relative_to(site):
                continue
            relative = target.relative_to(site).as_posix()
            if relative in owners:
                raise RuntimeControlError("runtime frozen RECORD ownership is ambiguous")
            owners[relative] = (
                *identity,
                cast(int, row["mode"]),
                cast(int, row["size_bytes"]),
                cast(str, row["sha256"]),
            )
    if not selected_owners or not owners:
        raise RuntimeControlError("runtime frozen authority is empty")
    return _IndependentRuntimeSubsetAuthority(
        extension_suffixes=tuple(importlib.machinery.EXTENSION_SUFFIXES),
        owners=owners,
        project_root=project_root,
        selected_owners=selected_owners,
        site=site,
    )


def _independent_validate_installed_mapping(
    root: Path,
    packages: tuple[dict[str, object], ...],
    mapped_destinations: dict[str, dict[str, object]],
) -> None:
    """Independently close mapped payloads against installed RECORD rows."""

    site = root / ".venv/lib/python3.12/site-packages"
    venv = root / ".venv"
    installed: dict[str, dict[str, object]] = {}
    for package in packages:
        owner = cast(str, package["name"])
        for row in cast(list[dict[str, object]], package["record_rows"]):
            if row.get("self") is True:
                continue
            relative = cast(str, row["path"])
            target = Path(os.path.normpath(os.fspath(site / relative)))
            if not target.is_relative_to(venv):
                raise RuntimeControlError("retained installed destination escapes venv")
            destination = target.relative_to(venv).as_posix()
            if destination in installed:
                raise RuntimeControlError("retained installed destinations collide")
            installed[destination] = {"owner": owner, "relative": relative, **row}
            parts = tuple(relative.split("/"))
            executable_scheme = (
                len(parts) == 5
                and parts[:4] == ("..", "..", "..", "bin")
                and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", parts[4]) is not None
            )
            if ".." in parts and not executable_scheme:
                mapped = mapped_destinations.get(destination)
                canonical_relative = os.path.relpath(venv / destination, site).replace(os.sep, "/")
                if mapped is None or relative != canonical_relative:
                    raise RuntimeControlError(
                        "retained external RECORD lacks exact PEP 427 mapping"
                    )
                if (
                    mapped["owner"] != owner
                    or mapped["sha256"] != row["sha256"]
                    or mapped["size_bytes"] != row["size_bytes"]
                    or mapped["mode"] != row["mode"]
                ):
                    raise RuntimeControlError("retained external mapping owner/bytes/mode differ")
    for destination, mapped in mapped_destinations.items():
        installed_row = installed.get(destination)
        if installed_row is None:
            raise RuntimeControlError("retained extracted payload lacks installed owner")
        if (
            installed_row["owner"] != mapped["owner"]
            or installed_row["sha256"] != mapped["sha256"]
            or installed_row["size_bytes"] != mapped["size_bytes"]
            or installed_row["mode"] != mapped["mode"]
        ):
            raise RuntimeControlError("retained extracted/installed mapping differs")


def _independent_require_global_site_ownership(
    physical_paths: set[str], owners: dict[str, str]
) -> None:
    """Independently close installed ownership around the two uv bootstrap files."""

    expected = set(owners) | {"_virtualenv.pth", "_virtualenv.py"}
    if physical_paths != expected:
        raise RuntimeControlError(
            "retained global installed ownership closure differs: "
            f"unowned={sorted(physical_paths - expected)}, "
            f"missing={sorted(expected - physical_paths)}"
        )


def _independent_site_editable_authority(
    root: Path,
    selected_records: tuple[dict[str, object], ...],
    repository: tuple[dict[str, object], ...],
    lock_inputs: dict[str, object],
) -> tuple[tuple[dict[str, object], ...], dict[str, object]]:
    site = root / ".venv/lib/python3.12/site-packages"
    venv = root / ".venv"
    scheme = sysconfig.get_paths(
        "venv",
        vars={
            key: os.fspath(venv)
            for key in ("base", "installed_base", "installed_platbase", "platbase")
        },
    )
    if (
        Path(scheme["purelib"]).resolve() != site.resolve()
        or Path(scheme["platlib"]).resolve() != site.resolve()
    ):
        raise RuntimeControlError("retained exact purelib/platlib roots differ")
    immediate = tuple(os.scandir(site))
    pth_names = sorted(entry.name for entry in immediate if entry.name.endswith(".pth"))
    if pth_names != ["_virtualenv.pth", "a1_coverage.pth", "scouting_intelligence.pth"]:
        raise RuntimeControlError("retained exact three-PTH census differs")
    if len({name.casefold() for name in pth_names}) != 3 or any(
        entry.name.endswith((".egg", ".egg-info")) for entry in immediate
    ):
        raise RuntimeControlError("retained PTH/egg closure differs")
    exact = {
        "_virtualenv.pth": (18, "69ac3d8f27e679c81b94ab30b3b56e9cd138219b1ba94a1fa3606d5a76a1433d"),
        "_virtualenv.py": (
            4_342,
            "6cf30c56faf2a55228914dbbd17f8088ed371ebb08f5e7fa6fd931f913fcaf1d",
        ),
        "a1_coverage.pth": (
            205,
            "ef2ed06d19867ec669c09a804060666a9cd5e383af0a9d11aa2de79b77d448e8",
        ),
    }
    bootstrap: list[dict[str, object]] = []
    for relative, (size, digest) in exact.items():
        raw = _absolute_regular(site / relative, mode=0o644)
        if len(raw) != size or _sha256(raw) != digest:
            raise RuntimeControlError("retained bootstrap/coverage bytes differ")
        bootstrap.append(
            {
                "mode": 0o644,
                "path": f".venv/lib/python3.12/site-packages/{relative}",
                "sha256": _sha256(raw),
                "size_bytes": len(raw),
            }
        )
    if _absolute_regular(site / "_virtualenv.pth", mode=0o644) != b"import _virtualenv":
        raise RuntimeControlError("retained uv bootstrap PTH literal differs")
    coverage = next(row for row in selected_records if row["name"] == "coverage")
    coverage_owner = [
        row
        for row in cast(list[dict[str, object]], coverage["record_rows"])
        if row["path"] == "a1_coverage.pth"
    ]
    if len(coverage_owner) != 1 or coverage_owner[0]["sha256"] != exact["a1_coverage.pth"][1]:
        raise RuntimeControlError("retained coverage hook ownership differs")

    dist_info = site / "scouting_intelligence-0.1.0.dist-info"
    if not dist_info.is_dir() or dist_info.is_symlink():
        raise RuntimeControlError("retained editable dist-info authority is unsafe")
    metadata_names = (
        "INSTALLER",
        "METADATA",
        "RECORD",
        "REQUESTED",
        "WHEEL",
        "direct_url.json",
        "uv_build.json",
        "uv_cache.json",
    )
    if tuple(sorted(entry.name for entry in os.scandir(dist_info))) != metadata_names:
        raise RuntimeControlError("retained editable metadata census differs")
    declarations = list(
        csv.reader(_absolute_regular(dist_info / "RECORD", mode=0o644).decode().splitlines())
    )
    expected_paths = {
        *(f"{dist_info.name}/{name}" for name in metadata_names),
        "scouting_intelligence.pth",
    }
    if len(declarations) != 9 or {row[0] for row in declarations} != expected_paths:
        raise RuntimeControlError("retained editable RECORD nine-row census differs")
    records: list[dict[str, object]] = []
    for relative, digest_cell, size_cell in declarations:
        if relative == f"{dist_info.name}/RECORD":
            if digest_cell or size_cell:
                raise RuntimeControlError("retained editable RECORD self row differs")
            records.append({"path": relative, "self": True})
            continue
        target = site / relative
        raw = _absolute_regular(target, mode=stat.S_IMODE(target.stat().st_mode))
        encoded = base64.urlsafe_b64encode(hashlib.sha256(raw).digest()).decode().rstrip("=")
        if digest_cell != f"sha256={encoded}" or size_cell != str(len(raw)):
            raise RuntimeControlError("retained editable RECORD target differs")
        records.append(
            {
                "mode": stat.S_IMODE(target.stat().st_mode),
                "path": relative,
                "sha256": _sha256(raw),
                "size_bytes": len(raw),
            }
        )
    exact_metadata = {
        "INSTALLER": (2, "e6184ce10e266134fdcfa401e8f1a95005bcd4f18d16b62b757323e2833fe9a9", b"uv"),
        "METADATA": (
            1_771,
            "ce423e8f2bde3826d54e952bf0c7059cdc426b2d4cd902e72e8dd91e8cd29351",
            None,
        ),
        "REQUESTED": (0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", b""),
        "WHEEL": (79, "45154ba95ba052614ea8179d0450260386ec8057113940624942a51118b41dc8", None),
        "uv_build.json": (
            2,
            "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a",
            b"{}",
        ),
    }
    for name, (size, digest, literal) in exact_metadata.items():
        raw = _absolute_regular(dist_info / name, mode=0o644)
        if len(raw) != size or _sha256(raw) != digest or (literal is not None and raw != literal):
            raise RuntimeControlError("retained editable stable metadata differs")
    pth_raw = _absolute_regular(site / "scouting_intelligence.pth", mode=0o644)
    if pth_raw != os.fspath(root / "src").encode():
        raise RuntimeControlError("retained editable PTH relation differs")
    normalized_pth = b"<W04_PROJECT_ROOT>/src"
    direct_raw = _absolute_regular(dist_info / "direct_url.json", mode=0o644)
    direct_expected = f'{{"url":"file://{root}","dir_info":{{"editable":true}}}}'.encode()
    if direct_raw != direct_expected or _load_strict_json(direct_raw) != {
        "url": f"file://{root}",
        "dir_info": {"editable": True},
    }:
        raise RuntimeControlError("retained editable direct_url relation differs")
    normalized_direct = b'{"url":"file://<W04_PROJECT_ROOT>","dir_info":{"editable":true}}'
    cache = _load_strict_json(_absolute_regular(dist_info / "uv_cache.json", mode=0o644))
    if type(cache) is not dict or set(cache) != {
        "timestamp",
        "commit",
        "tags",
        "env",
        "directories",
    }:
        raise RuntimeControlError("retained editable uv_cache keys differ")
    cache_object = cast(dict[str, object], cache)
    if (
        cache_object["commit"] is not None
        or cache_object["tags"] is not None
        or cache_object["env"] != {}
        or set(cast(dict[str, object], cache_object["directories"])) != {"src"}
    ):
        raise RuntimeControlError("retained editable uv_cache structure differs")
    for clock in (
        cache_object["timestamp"],
        cast(dict[str, object], cache_object["directories"])["src"],
    ):
        if (
            type(clock) is not dict
            or set(cast(dict[str, object], clock)) != {"secs_since_epoch", "nanos_since_epoch"}
            or any(type(value) is not int for value in cast(dict[str, object], clock).values())
        ):
            raise RuntimeControlError("retained editable uv_cache clock shape differs")
    normalized_cache = _canonical_json_bytes(
        {
            "commit": None,
            "directories": ["src"],
            "env": {},
            "tags": None,
            "timestamp_policy": "operational-excluded",
        }
    )
    normalized = {
        "scouting_intelligence.pth": normalized_pth,
        f"{dist_info.name}/direct_url.json": normalized_direct,
        f"{dist_info.name}/uv_cache.json": normalized_cache,
    }
    stable_records = tuple(
        row
        if cast(str, row["path"]) not in normalized
        else {
            "mode": row["mode"],
            "normalization": "ROOT_OR_CLOCK_EXACT",
            "path": row["path"],
            "sha256": _sha256(normalized[cast(str, row["path"])]),
            "size_bytes": len(normalized[cast(str, row["path"])]),
        }
        for row in records
    )
    owners: dict[str, str] = {}
    for package in selected_records:
        owner = f"{package['name']}=={package['version']}"
        for row in cast(list[dict[str, object]], package["record_rows"]):
            target = Path(os.path.normpath(os.fspath(site / cast(str, row["path"]))))
            if target.is_relative_to(site):
                key = target.relative_to(site).as_posix()
                if key in owners:
                    raise RuntimeControlError("retained installed file has multiple owners")
                owners[key] = owner
    for row in records:
        key = cast(str, row["path"])
        if key in owners:
            raise RuntimeControlError("retained editable file has multiple owners")
        owners[key] = "scouting-intelligence==0.1.0"
    physical: set[str] = set()
    for directory, names, files in os.walk(site, topdown=True, followlinks=False):
        names[:] = sorted(name for name in names if name != "__pycache__")
        for name in sorted(files):
            if name.lower().endswith((".pyc", ".pyo")):
                continue
            path = Path(directory, name)
            if path.is_symlink() or not path.is_file():
                raise RuntimeControlError("retained installed site contains nonregular authority")
            physical.add(path.relative_to(site).as_posix())
    _independent_require_global_site_ownership(physical, owners)
    detail = {
        "algorithm": "w04-editable-root-stable-v2",
        "identity": {"name": "scouting-intelligence", "source": ".", "version": "0.1.0"},
        "lock_inputs": lock_inputs,
        "normalized_record_rows": stable_records,
        "pyproject_sha256": lock_inputs["pyproject_sha256"],
        "repository_rows": repository,
        "uv_cache_policy": "exact-keys-commit-tags-null-env-empty-src-clock-excluded-v1",
    }
    return tuple(bootstrap), detail


_WRAPPER_AUTHORITY: Final = {
    "bandit": ("python", "367ffc02238517c99e118c4f420e87b86cc8d5c3dc759af41e1ce2a9fc8153f7", 306),
    "bandit-baseline": (
        "python",
        "91146787220a7c3484e6eb35dd35e7e889d3b04e92509656f549b72a8ed77851",
        310,
    ),
    "bandit-config-generator": (
        "python",
        "173766f408c34f6386d770aacb53a40d297b50d8795ad0db1757f9f91f37172e",
        318,
    ),
    "coverage": ("python", "bb4cc36b14cb2023526289e6232b8790cf8f164c970d343529d5e403dfba80d1", 307),
    "coverage-3.12": (
        "python",
        "d48a554ea733bb6ddc405be0913b58d299814a72ea0200878e61bb4e7030acf8",
        329,
    ),
    "coverage3": (
        "python",
        "d48a554ea733bb6ddc405be0913b58d299814a72ea0200878e61bb4e7030acf8",
        329,
    ),
    "detect-secrets": (
        "python3",
        "65568bb4e64ef69d1a74e1248bfe4b4f19b8b23761ac1a7624dff023cccb3820",
        311,
    ),
    "detect-secrets-hook": (
        "python3",
        "11eb91f23986109ae8951d496ae02425328585987cb531d819ac4b5a288faa2a",
        322,
    ),
    "dmypy": ("python", "be03adaa9f022b218346392c16409b70924b77fa74d9e55b927f57d1f13604f9", 326),
    "doesitcache": (
        "python",
        "350c6237ba2a59f4628984b287704e78c067702c315de2ad429fd291d4c06344",
        308,
    ),
    "f2py": ("python", "c57d802cf5d7828736d7c09d85578c5c16fcbb0de8329be9ae02da29455bee75", 308),
    "fastapi": ("python", "735d762fc7ad9bb11b22beb9c08dff373b0b2a876f24b3df13fdc102a031c101", 302),
    "httpx": ("python3", "498e042170d32117204f4897655dc70339fe3f544d093d0feac546b21b4452e4", 297),
    "hypothesis": (
        "python",
        "3c0e7bf806e3002c4297914cfca1e57ce2e42d585db4d9f9204a3abc88b44df7",
        311,
    ),
    "idna": ("python", "800fe2c5d8d17b9911ae4fce3144937643245735c606315719ea2a67150f8ffb", 299),
    "import-linter": (
        "python",
        "08d8a9c9bdc6f014eead88f66a24128c65a32f840d4e46c13efa8db808d94dbc",
        325,
    ),
    "lint-imports": (
        "python",
        "accc249155c97dac1b8ead4697cf287871aa848127c6612f279c94c2b5a660b9",
        339,
    ),
    "markdown-it": (
        "python",
        "c277f573e357e50fd8e818c646bb82678190de1d2ab1455223807a859fca975a",
        312,
    ),
    "mypy": ("python", "b7afb7c6a60c64b41be80fd2b9877101586b1c2f2c4ccd45901b790bc54855f7", 322),
    "mypyc": ("python", "692346d9a80220988c7aa95fbf09933005d159f36b759f4404fd12afd3973815", 305),
    "normalizer": (
        "python",
        "afaef6b07c7bc80f306a9f8657ff36cf31e21e702975bbc92daa154830672597",
        325,
    ),
    "numpy-config": (
        "python",
        "f1a23cdc2ba423a6c22d65c048f6cece2d055c02f1c24a8caa1456fe373df410",
        308,
    ),
    "pip": ("python", "8f26d19e3c0577a0a1d0e0798f5b3f84b1f8a90ef499b0512b3df881837e6576", 313),
    "pip-audit": (
        "python",
        "916cd2b2fec550634a7c17baec1913ba254d49d3aa60185e69e8332bac8e0ade",
        307,
    ),
    "pip-licenses": (
        "python3",
        "371a4708d778c83fee484dcef32c72dbf54680ce5de3d5995313e0a0ff34841a",
        303,
    ),
    "pip3": ("python", "8f26d19e3c0577a0a1d0e0798f5b3f84b1f8a90ef499b0512b3df881837e6576", 313),
    "pip3.12": ("python", "8f26d19e3c0577a0a1d0e0798f5b3f84b1f8a90ef499b0512b3df881837e6576", 313),
    "playwright": (
        "python",
        "f024dd05a918cae7b5bf24603c94920e51b506018992af5332e183e41fc880df",
        310,
    ),
    "py.test": ("python", "3a8b91b74fcd05e761ff46d58240829b76c5c5f368d0335e9f2184f648c26b36", 323),
    "pygmentize": (
        "python",
        "a3bdb4a2937fe22d05b2dc5b66e8aa291b6e39a69c46f52708ae5aa198183d21",
        307,
    ),
    "pytest": ("python", "3a8b91b74fcd05e761ff46d58240829b76c5c5f368d0335e9f2184f648c26b36", 323),
    "stubgen": ("python", "a56dfd8a967a208711d5c111413f0bfbe86d01a2e34daf8ff5dc12ebacf3077c", 303),
    "stubtest": ("python", "44ea3c1bb2016243a57e60b8517f8e98d0f263909e1da147262d8754049203cf", 304),
    "uvicorn": ("python", "58aa69f472e934ea26e1c217853516b9ea28b3f4559d807b5a8699faab659f93", 303),
}


def _independent_stable_records(
    root: Path, packages: tuple[dict[str, object], ...]
) -> tuple[dict[str, object], ...]:
    bin_rows: dict[str, dict[str, object]] = {}
    for package in packages:
        for row in cast(list[dict[str, object]], package["record_rows"]):
            path = cast(str, row["path"])
            if path.startswith("../../../bin/"):
                bin_rows[path.removeprefix("../../../bin/")] = row
    if set(bin_rows) != {*_WRAPPER_AUTHORITY, "ruff"} or len(bin_rows) != 35:
        raise RuntimeControlError("retained executable census differs")
    replacements: dict[str, dict[str, object]] = {}
    for name, (alias, digest, size) in _WRAPPER_AUTHORITY.items():
        raw = _absolute_regular(root / ".venv/bin" / name, mode=0o755)
        first, separator, body = raw.partition(b"\n")
        if first != f"#!{root}/.venv/bin/{alias}".encode() or separator != b"\n":
            raise RuntimeControlError("retained executable selected alias differs")
        token = "W04_VENV_WRAPPER_PYTHON3" if alias == "python3" else "W04_VENV_WRAPPER_PYTHON"
        normalized = f"#!<{token}>\n".encode() + body
        if _sha256(normalized) != digest or len(normalized) != size:
            raise RuntimeControlError("retained normalized wrapper authority differs")
        original = bin_rows[name]
        replacements[cast(str, original["path"])] = {
            "mode": 0o755,
            "normalization_role": alias,
            "path": original["path"],
            "sha256": digest,
            "size_bytes": size,
        }
    ruff = _absolute_regular(root / ".venv/bin/ruff", mode=0o755)
    if (
        len(ruff) != 23_669_488
        or _sha256(ruff) != "1ac190f23d9a690d75b3e74eb88a07e02f6414227a41ba1920609af989ecec52"
    ):
        raise RuntimeControlError("retained Ruff wheel-script authority differs")
    stable: list[dict[str, object]] = []
    for package in packages:
        stable.append(
            {
                "name": package["name"],
                "record_rows": [
                    replacements.get(cast(str, row["path"]), row)
                    for row in cast(list[dict[str, object]], package["record_rows"])
                ],
                "version": package["version"],
            }
        )
    return tuple(stable)


def _independent_executable_rows(
    root: Path, packages: tuple[dict[str, object], ...]
) -> tuple[dict[str, object], ...]:
    direct: dict[str, tuple[str, str, str, str]] = {}
    owners: dict[str, tuple[str, str, dict[str, object]]] = {}
    site = root / ".venv/lib/python3.12/site-packages"
    for package in packages:
        owner, version = cast(str, package["name"]), cast(str, package["version"])
        package_rows = cast(list[dict[str, object]], package["record_rows"])
        for record in package_rows:
            path = cast(str, record["path"])
            if path.startswith("../../../bin/"):
                owners[path.removeprefix("../../../bin/")] = (owner, version, record)
        entry_rows = [
            row
            for row in package_rows
            if cast(str, row["path"]).endswith(".dist-info/entry_points.txt")
        ]
        if not entry_rows:
            continue
        if len(entry_rows) != 1:
            raise RuntimeControlError("retained entry-point authority is not singular")
        entry = entry_rows[0]
        raw = _absolute_regular(site / cast(str, entry["path"]), mode=cast(int, entry["mode"]))
        parser = configparser.ConfigParser(interpolation=None, strict=True)
        parser.optionxform = lambda option: option  # type: ignore[method-assign,assignment]
        parser.read_string(raw.decode("utf-8", errors="strict"))
        for group in ("console_scripts", "gui_scripts"):
            if parser.has_section(group):
                for name, target in parser.items(group):
                    if name in direct:
                        raise RuntimeControlError("retained direct entry point is duplicated")
                    direct[name] = (owner, version, group, target)
    if len(direct) != 33 or set(owners) != {*_WRAPPER_AUTHORITY, "ruff"}:
        raise RuntimeControlError("retained executable constructive authority differs")
    rows: list[dict[str, object]] = []
    for name in sorted(owners):
        owner, version, record = owners[name]
        if name == "ruff":
            raw = _absolute_regular(root / ".venv/bin/ruff", mode=0o755)
            rows.append(
                {
                    "authority_class": "W",
                    "mode": 0o755,
                    "name": "ruff",
                    "owner": "ruff==0.16.0",
                    "record_path": record["path"],
                    "sha256": _sha256(raw),
                    "size_bytes": len(raw),
                    "source": "ruff-0.16.0.data/scripts/ruff",
                }
            )
            continue
        alias, digest, size = _WRAPPER_AUTHORITY[name]
        authority = "P" if name == "pip3.12" else "E"
        if authority == "P":
            group, target = "derived-pip-interpreter-version-alias", "pip._internal.cli.main:main"
        else:
            declared_owner, declared_version, group, target = direct[name]
            if (owner, version) != (declared_owner, declared_version):
                raise RuntimeControlError("retained entry-point wrapper owner differs")
        rows.append(
            {
                "authority_class": authority,
                "entry_point_group": group,
                "mode": 0o755,
                "name": name,
                "normalized_sha256": digest,
                "normalized_size_bytes": size,
                "owner": f"{owner}=={version}",
                "record_path": record["path"],
                "selected_alias": alias,
                "target": target,
            }
        )
    if (
        sum(row["authority_class"] == "E" for row in rows) != 33
        or sum(row["authority_class"] == "P" for row in rows) != 1
        or sum(row["authority_class"] == "W" for row in rows) != 1
        or len({row["owner"] for row in rows}) != 21
        or sum(row.get("selected_alias") == "python" for row in rows) != 30
        or sum(row.get("selected_alias") == "python3" for row in rows) != 4
    ):
        raise RuntimeControlError("retained executable class cardinalities differ")
    return tuple(rows)


def _independent_selector_closure_wheels(
    root: Path,
    preliminary: tuple[dict[str, object], ...],
    records: tuple[dict[str, object], ...],
) -> tuple[dict[str, object], tuple[dict[str, object], ...], tuple[dict[str, object], ...]]:
    site = root / ".venv/lib/python3.12/site-packages"
    if os.fspath(site) not in sys.path:
        sys.path.insert(0, os.fspath(site))
    from packaging.markers import Marker, default_environment
    from packaging.tags import sys_tags
    from packaging.utils import canonicalize_name, parse_wheel_filename
    from packaging.version import Version

    marker_environment = cast(dict[str, str], dict(default_environment()))
    tag_values = tuple(sys_tags())
    ordered_tags = tuple(str(tag) for tag in tag_values)
    if len(ordered_tags) != 1230 or len(set(ordered_tags)) != len(ordered_tags):
        raise RuntimeControlError("retained complete compatible-tag order differs")
    parsed = tomllib.loads(
        _guard_read_relative(root, "uv.lock", max_bytes=128 * 1024 * 1024).decode()
    )
    packages = cast(list[dict[str, object]], parsed["package"])
    by_name = {cast(str, package["name"]): package for package in packages}
    groups = ("data", "e2e", "lint-type", "model", "orchestration", "runtime", "security", "test")
    dev = cast(
        dict[str, list[dict[str, object]]], by_name["scouting-intelligence"]["dev-dependencies"]
    )
    if tuple(sorted(dev)) != groups:
        raise RuntimeControlError("retained dependency-group roster differs")
    queue: list[tuple[str, str, tuple[str, ...]]] = [
        (cast(str, edge["name"]), f"scouting-intelligence[{group}]", tuple())
        for group in groups
        for edge in dev[group]
    ]
    parents: dict[str, set[str]] = {}
    selected_extras: dict[str, set[str]] = {}
    while queue:
        name, parent, extras = queue.pop(0)
        package = by_name[name]
        parents.setdefault(name, set()).add(parent)
        new_extras = set(extras) - selected_extras.setdefault(name, set())
        first = len(parents[name]) == 1
        if not first and not new_extras:
            continue
        if first:
            for edge in cast(list[dict[str, object]], package.get("dependencies", [])):
                marker = edge.get("marker")
                if marker is not None and not Marker(cast(str, marker)).evaluate(
                    marker_environment
                ):
                    continue
                queue.append(
                    (
                        cast(str, edge["name"]),
                        name,
                        tuple(cast(list[str], edge.get("extra", []))),
                    )
                )
        optional = cast(
            dict[str, list[dict[str, object]]], package.get("optional-dependencies", {})
        )
        for extra in sorted(new_extras):
            if extra not in optional:
                raise RuntimeControlError("retained selected extra differs")
            queue.extend(
                (cast(str, edge["name"]), f"{name}[{extra}]", tuple()) for edge in optional[extra]
            )
    if set(parents) != {cast(str, row["name"]) for row in preliminary}:
        raise RuntimeControlError("retained marker/extra closure differs from installed")
    ranks = {tag: index for index, tag in enumerate(tag_values)}
    closure: list[dict[str, object]] = []
    wheels: list[dict[str, object]] = []
    for name in sorted(parents):
        package = by_name[name]
        version = cast(str, package["version"])
        candidates: list[tuple[int, dict[str, object], str, list[str]]] = []
        for wheel in cast(list[dict[str, object]], package.get("wheels", [])):
            filename = Path(urllib.parse.urlparse(cast(str, wheel["url"])).path).name
            parsed_name, parsed_version, _build, tags = parse_wheel_filename(filename)
            if canonicalize_name(parsed_name) != name or Version(str(parsed_version)) != Version(
                version
            ):
                raise RuntimeControlError("retained wheel filename identity differs")
            compatible = [ranks[tag] for tag in tags if tag in ranks]
            if compatible:
                candidates.append(
                    (min(compatible), wheel, filename, sorted(str(tag) for tag in tags))
                )
        best_rank = min(candidate[0] for candidate in candidates)
        best = [candidate for candidate in candidates if candidate[0] == best_rank]
        if len(best) != 1:
            raise RuntimeControlError("retained compatible-wheel selector is not singular")
        rank, wheel, filename, declared_tags = best[0]
        wheel_row = {
            "declared_tags": declared_tags,
            "filename": filename,
            "lock_hash": wheel["hash"],
            "lock_size": wheel["size"],
            "name": name,
            "rank": rank,
            "version": version,
        }
        wheels.append(wheel_row)
        closure.append(
            {
                "extras": sorted(selected_extras[name]),
                "name": name,
                "parents": sorted(parents[name]),
                "source": package["source"],
                "version": version,
                "wheel": wheel_row,
            }
        )
    packaging_record = next(row for row in records if row["name"] == "packaging")
    selector: dict[str, object] = {
        "algorithm": "w04-packaging-tag-bootstrap-v1",
        "imported_packaging_modules": [
            "packaging",
            "packaging._elffile",
            "packaging._manylinux",
            "packaging._musllinux",
            "packaging._parser",
            "packaging._tokenizer",
            "packaging.markers",
            "packaging.specifiers",
            "packaging.tags",
            "packaging.utils",
            "packaging.version",
        ],
        "marker_environment": {key: marker_environment[key] for key in sorted(marker_environment)},
        "ordered_tags": list(ordered_tags),
        "packaging_record_sha256": _sha256_json(packaging_record),
        "packaging_version": "26.2",
    }
    return selector, tuple(closure), tuple(wheels)


def _independent_pyc_detail(
    root: Path,
    packages: tuple[dict[str, object], ...],
    repository: tuple[dict[str, object], ...],
    bootstrap: tuple[dict[str, object], ...],
) -> dict[str, object]:
    sources: list[dict[str, object]] = []
    for package in packages:
        owner = f"{package['name']}=={package['version']}"
        for record in cast(list[dict[str, object]], package["record_rows"]):
            path = cast(str, record["path"])
            if path.endswith(".py"):
                stem = Path(path).stem
                sources.append(
                    {
                        "authority_class": "SELECTED_DISTRIBUTION_RECORD",
                        "normal_cache_name": f"{stem}.cpython-312[.opt-0|.opt-1|.opt-2].pyc",
                        "owner": owner,
                        "path": path,
                        "pytest_cache_name": f"{stem}.cpython-312-pytest-9.1.1.pyc",
                        "sha256": record["sha256"],
                        "size_bytes": record["size_bytes"],
                    }
                )
    for record in repository:
        path = cast(str, record["path"])
        if path.endswith(".py") and record.get("state") != "AUTHORIZED_ABSENT":
            stem = Path(path).stem
            sources.append(
                {
                    "authority_class": "REPOSITORY_CODE_MANIFEST",
                    "normal_cache_name": f"{stem}.cpython-312[.opt-0|.opt-1|.opt-2].pyc",
                    "owner": path,
                    "path": path,
                    "pytest_cache_name": f"{stem}.cpython-312-pytest-9.1.1.pyc",
                    "sha256": record["sha256"],
                    "size_bytes": record["size_bytes"],
                }
            )
    virtualenv = next(
        row for row in bootstrap if cast(str, row["path"]).endswith("/_virtualenv.py")
    )
    sources.append(
        {
            "authority_class": "UV_VENV_BOOTSTRAP",
            "normal_cache_name": "_virtualenv.cpython-312[.opt-0|.opt-1|.opt-2].pyc",
            "owner": "uv==0.9.21",
            "path": "_virtualenv.py",
            "pytest_cache_name": None,
            "sha256": virtualenv["sha256"],
            "size_bytes": virtualenv["size_bytes"],
        }
    )
    sources.sort(key=_canonical_json_bytes)
    predicates = (
        (
            "SITE_SIX_OPTIONAL_INERT_ORPHAN",
            "__pycache__/six.cpython-312.pyc",
            41_388,
            "4e59431b1d92fe443cbdb1f76e065ece05b1c4f6cb4925168be8e9321f390e28",
            "six.py",
            "SELECTED_SITE_PACKAGES",
        ),
        (
            "REPOSITORY_MIGRATIONS_ENV_OPTIONAL_INERT_ORPHAN",
            "migrations/__pycache__/env.cpython-312.pyc",
            2_795,
            "6d93fd4b51bfcfaed59e59358f6694fef65bf04be088e7ff8377340389990ff2",
            "migrations/env.py",
            "WHOLE_REPOSITORY",
        ),
        (
            "REPOSITORY_MIGRATIONS_FOUNDATION_OPTIONAL_INERT_ORPHAN",
            "migrations/versions/__pycache__/0001_foundation.cpython-312.pyc",
            25_415,
            "b10987536a062b17702b1fdb5dbb94ca0b2293f8c6d91e43a9fd4042dfeea84d",
            "migrations/versions/0001_foundation.py",
            "WHOLE_REPOSITORY",
        ),
        (
            "REPOSITORY_POSTGRES_OPTIONAL_INERT_ORPHAN",
            "src/scouting/storage/__pycache__/postgres.cpython-312.pyc",
            4_230,
            "ee3ae9a1dd7a942474cf6442c414d1d046aa8532d0e6702698bd19da46ff40ac",
            "src/scouting/storage/postgres.py",
            "WHOLE_REPOSITORY",
        ),
    )
    orphan_rows = tuple(
        {
            "authority_class": authority,
            "cache_path": cache_path,
            "expected_mode": 0o644,
            "expected_sha256": digest,
            "expected_size_bytes": size,
            "source_path": source,
            "source_required_absent": True,
            "traversal_root_role": role,
        }
        for authority, cache_path, size, digest, source, role in predicates
    )
    foreign_predicates = (
        {
            "authority_class": "REPOSITORY_FOREIGN_CACHE_TAG_DENIED",
            "cache_path": ("scripts/__pycache__/admit_wyscout_v5_runtime.cpython-314.pyc"),
            "cache_tag": "cpython-314",
            "denial_policy": "FOREIGN_INTERPRETER_TAG_DENIED_ZERO_READ",
            "expected_mode": 0o644,
            "expected_size_bytes": 190_312,
            "source_authority_required": "REPOSITORY_CODE_MANIFEST",
            "source_path": "scripts/admit_wyscout_v5_runtime.py",
            "traversal_root_role": "WHOLE_REPOSITORY",
        },
    )
    foreign_source = cast(str, foreign_predicates[0]["source_path"])
    foreign_source_rows = [row for row in sources if row["path"] == foreign_source]
    if (
        len(foreign_source_rows) != 1
        or foreign_source_rows[0]["authority_class"] != "REPOSITORY_CODE_MANIFEST"
    ):
        raise RuntimeControlError("foreign-tag denied PYC source authority differs")
    return {
        "algorithm": "w10-preexisting-pyc-enumerate-deny-audit-v1",
        "cache_tag": "cpython-312",
        "foreign_cache_tag_denial_predicates": foreign_predicates,
        "magic_hex": "cb0d0d0a",
        "normal_grammar": "<stem>.cpython-312[.opt-0|.opt-1|.opt-2].pyc",
        "no_cleanup": True,
        "orphan_predicates": orphan_rows,
        "post_w04_audit_only_source_paths": _derive_post_w04_audit_only_pyc_source_paths(
            root,
            frozenset(
                cast(str, row["path"])
                for row in sources
                if row["authority_class"] == "REPOSITORY_CODE_MANIFEST"
            ),
        ),
        "post_w04_retired_audit_only_pyc_predicates": (_POST_W04_RETIRED_AUDIT_ONLY_PYC_PREDICATES),
        "pytest_grammar": "<stem>.cpython-312-pytest-9.1.1.pyc",
        "pytest_version": "9.1.1",
        "source_rows": tuple(sources),
        "traversal_root_roles": ["SELECTED_SITE_PACKAGES", "WHOLE_REPOSITORY"],
        "zero_in_place_pyc_change": True,
        "zero_python_role_pyc_read": True,
    }


def _independent_pyc_inventory(
    root: Path, policy: dict[str, object]
) -> tuple[dict[str, object], ...]:
    """Classify every in-place PYC by no-follow metadata without reading it."""

    site = root / ".venv/lib/python3.12/site-packages"
    source_rows = cast(tuple[dict[str, object], ...], policy["source_rows"])
    site_sources = {
        cast(str, row["path"]): row
        for row in source_rows
        if row["authority_class"] in {"SELECTED_DISTRIBUTION_RECORD", "UV_VENV_BOOTSTRAP"}
    }
    repository_sources = {
        cast(str, row["path"]): row
        for row in source_rows
        if row["authority_class"] == "REPOSITORY_CODE_MANIFEST"
    }
    audit_only_rows = policy.get("post_w04_audit_only_source_paths")
    expected_audit_only_rows = _derive_post_w04_audit_only_pyc_source_paths(
        root,
        frozenset(repository_sources),
    )
    if type(audit_only_rows) is not tuple or _canonical_json_bytes(
        audit_only_rows
    ) != _canonical_json_bytes(expected_audit_only_rows):
        missing = tuple(
            sorted(
                set(expected_audit_only_rows) - set(cast(tuple[str, ...], audit_only_rows or ()))
            )
        )
        unexpected = tuple(
            sorted(
                set(cast(tuple[str, ...], audit_only_rows or ())) - set(expected_audit_only_rows)
            )
        )
        raise RuntimeControlError(
            "post-W04 audit-only PYC source roster differs from derived Python sources; "
            f"missing={missing!r}; unexpected={unexpected!r}"
        )
    audit_only_sources = set(cast(tuple[str, ...], audit_only_rows))
    retired_rows = policy.get("post_w04_retired_audit_only_pyc_predicates")
    if type(retired_rows) is not tuple or _canonical_json_bytes(
        retired_rows
    ) != _canonical_json_bytes(_POST_W04_RETIRED_AUDIT_ONLY_PYC_PREDICATES):
        raise RuntimeControlError("post-W04 retired audit-only PYC predicate differs")
    retired_predicates = cast(tuple[dict[str, object], ...], retired_rows)
    retired_by_path = {cast(str, row["cache_path"]): row for row in retired_predicates}
    if len(retired_by_path) != len(retired_predicates):
        raise RuntimeControlError("post-W04 retired audit-only PYC predicate is duplicated")
    for predicate in retired_predicates:
        if (root / cast(str, predicate["source_path"])).exists():
            raise RuntimeControlError("post-W04 retired PYC regained its source path")
    expected_foreign_rows = (
        {
            "authority_class": "REPOSITORY_FOREIGN_CACHE_TAG_DENIED",
            "cache_path": ("scripts/__pycache__/admit_wyscout_v5_runtime.cpython-314.pyc"),
            "cache_tag": "cpython-314",
            "denial_policy": "FOREIGN_INTERPRETER_TAG_DENIED_ZERO_READ",
            "expected_mode": 0o644,
            "expected_size_bytes": 190_312,
            "source_authority_required": "REPOSITORY_CODE_MANIFEST",
            "source_path": "scripts/admit_wyscout_v5_runtime.py",
            "traversal_root_role": "WHOLE_REPOSITORY",
        },
    )
    foreign_rows = policy.get("foreign_cache_tag_denial_predicates")
    if type(foreign_rows) is not tuple or _canonical_json_bytes(
        foreign_rows
    ) != _canonical_json_bytes(expected_foreign_rows):
        raise RuntimeControlError("foreign-tag denied PYC predicate differs")
    foreign_predicates = cast(tuple[dict[str, object], ...], foreign_rows)
    foreign_by_path = {cast(str, row["cache_path"]): row for row in foreign_predicates}
    if len(foreign_by_path) != len(foreign_predicates):
        raise RuntimeControlError("foreign-tag denied PYC predicate is duplicated")
    foreign_source = cast(str, foreign_predicates[0]["source_path"])
    foreign_source_rows = [
        row
        for row in source_rows
        if row.get("path") == foreign_source
        and row.get("authority_class") == "REPOSITORY_CODE_MANIFEST"
    ]
    if len(foreign_source_rows) != 1:
        raise RuntimeControlError("foreign-tag denied PYC source authority differs")
    foreign_source_row = foreign_source_rows[0]
    if (
        frozenset(foreign_source_row)
        != {
            "authority_class",
            "normal_cache_name",
            "owner",
            "path",
            "pytest_cache_name",
            "sha256",
            "size_bytes",
        }
        or foreign_source_row["owner"] != foreign_source
        or foreign_source_row["normal_cache_name"]
        != "admit_wyscout_v5_runtime.cpython-312[.opt-0|.opt-1|.opt-2].pyc"
        or foreign_source_row["pytest_cache_name"]
        != "admit_wyscout_v5_runtime.cpython-312-pytest-9.1.1.pyc"
        or type(foreign_source_row["sha256"]) is not str
        or SHA256_RE.fullmatch(foreign_source_row["sha256"]) is None
        or type(foreign_source_row["size_bytes"]) is not int
    ):
        raise RuntimeControlError("foreign-tag denied PYC source row differs")
    try:
        foreign_source_metadata = os.lstat(root / foreign_source)
    except OSError as exc:
        raise RuntimeControlError("foreign-tag denied PYC source path differs") from exc
    if (
        not stat.S_ISREG(foreign_source_metadata.st_mode)
        or stat.S_ISLNK(foreign_source_metadata.st_mode)
        or stat.S_IMODE(foreign_source_metadata.st_mode) != 0o644
        or foreign_source_metadata.st_nlink != 1
        or foreign_source_metadata.st_size != foreign_source_row["size_bytes"]
    ):
        raise RuntimeControlError("foreign-tag denied PYC source path differs")
    orphan_rows = cast(tuple[dict[str, object], ...], policy["orphan_predicates"])
    site_orphans = {
        cast(str, row["cache_path"]): row
        for row in orphan_rows
        if row["traversal_root_role"] == "SELECTED_SITE_PACKAGES"
    }
    repository_orphans = {
        cast(str, row["cache_path"]): row
        for row in orphan_rows
        if row["traversal_root_role"] == "WHOLE_REPOSITORY"
    }
    for predicate in orphan_rows:
        predicate_source = cast(str, predicate["source_path"])
        candidate = (
            site / predicate_source
            if predicate["traversal_root_role"] == "SELECTED_SITE_PACKAGES"
            else root / predicate_source
        )
        if candidate.exists():
            raise RuntimeControlError("optional inert PYC orphan gained a source sibling")
    inventory: list[dict[str, object]] = []
    seen_foreign_paths: set[str] = set()
    normal = re.compile(r"^(?P<stem>.+)\.cpython-312(?:\.opt-[012])?\.pyc$")
    pytest_name = re.compile(r"^(?P<stem>.+)\.cpython-312-pytest-9\.1\.1\.pyc$")
    foreign_normal = re.compile(r"^(?P<stem>.+)\.(?P<tag>cpython-[0-9]+)(?:\.opt-[012])?\.pyc$")
    foreign_pytest = re.compile(
        r"^(?P<stem>.+)\.(?P<tag>cpython-[0-9]+)-pytest-[0-9]+"
        r"(?:\.[0-9]+){1,2}\.pyc$"
    )
    for traversal_root, role, sources, orphans in (
        (site, "SELECTED_SITE_PACKAGES", site_sources, site_orphans),
        (root, "WHOLE_REPOSITORY", repository_sources, repository_orphans),
    ):
        for directory, names, files in os.walk(traversal_root, topdown=True, followlinks=False):
            if role == "WHOLE_REPOSITORY" and Path(directory) == root:
                names[:] = [name for name in names if name != ".venv"]
            for name in names:
                path = Path(directory, name)
                if path.is_symlink():
                    raise RuntimeControlError("PYC traversal contains a directory symlink")
            names.sort()
            if Path(directory).name == "__pycache__":
                metadata = os.lstat(directory)
                if (
                    not stat.S_ISDIR(metadata.st_mode)
                    or stat.S_ISLNK(metadata.st_mode)
                    or stat.S_IMODE(metadata.st_mode) != 0o755
                ):
                    raise RuntimeControlError("PYC cache-directory metadata differs")
                inventory.append(
                    {
                        "ctime_ns": metadata.st_ctime_ns,
                        "device": metadata.st_dev,
                        "entry_kind": "CACHE_DIRECTORY",
                        "inode": metadata.st_ino,
                        "link_count": metadata.st_nlink,
                        "mode": stat.S_IMODE(metadata.st_mode),
                        "mtime_ns": metadata.st_mtime_ns,
                        "path": Path(directory).relative_to(traversal_root).as_posix(),
                        "role": role,
                        "size_bytes": metadata.st_size,
                    }
                )
            for name in sorted(files):
                if name.endswith(".pyo"):
                    raise RuntimeControlError("PYC traversal contains optimized bytecode")
                if not name.endswith(".pyc"):
                    continue
                path = Path(directory, name)
                relative = path.relative_to(traversal_root).as_posix()
                metadata = os.lstat(path)
                if (
                    not stat.S_ISREG(metadata.st_mode)
                    or stat.S_ISLNK(metadata.st_mode)
                    or stat.S_IMODE(metadata.st_mode) != 0o644
                    or metadata.st_nlink != 1
                ):
                    raise RuntimeControlError("PYC lstat metadata differs")
                orphan = orphans.get(relative)
                if orphan is not None:
                    if metadata.st_size != orphan["expected_size_bytes"] or metadata.st_size < 16:
                        raise RuntimeControlError("optional inert PYC orphan size differs")
                    authority = orphan["authority_class"]
                    source_path = None
                    source_authority = None
                    classification_fields: dict[str, object] = {}
                else:
                    if path.parent.name != "__pycache__":
                        raise RuntimeControlError("PYC is outside an exact cache directory")
                    foreign = foreign_by_path.get(relative) if role == "WHOLE_REPOSITORY" else None
                    if foreign is not None:
                        if (
                            metadata.st_size != foreign["expected_size_bytes"]
                            or stat.S_IMODE(metadata.st_mode) != foreign["expected_mode"]
                        ):
                            raise RuntimeControlError("foreign-tag denied PYC metadata differs")
                        authority = foreign["authority_class"]
                        source_path = foreign["source_path"]
                        source_authority = None
                        classification_fields = {
                            "denial_policy": foreign["denial_policy"],
                            "foreign_cache_tag": foreign["cache_tag"],
                            "source_authority_required": foreign["source_authority_required"],
                        }
                        seen_foreign_paths.add(relative)
                    else:
                        retired = (
                            retired_by_path.get(relative) if role == "WHOLE_REPOSITORY" else None
                        )
                        if retired is not None:
                            if metadata.st_size < 16:
                                raise RuntimeControlError("post-W04 retired PYC metadata differs")
                            authority = retired["authority_class"]
                            source_path = retired["source_path"]
                            source_authority = None
                            classification_fields = {
                                "authority_scope": "AUDIT_ONLY_ZERO_READ_USE",
                                "denial_policy": retired["denial_policy"],
                                "source_required_absent": True,
                            }
                        else:
                            match = pytest_name.fullmatch(name)
                            rewrite = match is not None
                            if match is None:
                                match = normal.fullmatch(name)
                            if match is not None:
                                source_path = (
                                    (path.parent.parent / f"{match.group('stem')}.py")
                                    .relative_to(traversal_root)
                                    .as_posix()
                                )
                                if source_path in sources:
                                    source_authority = cast(
                                        str, sources[source_path]["authority_class"]
                                    )
                                    if source_authority == "UV_VENV_BOOTSTRAP":
                                        authority = "UV_BOOTSTRAP_NORMAL"
                                    elif role == "SELECTED_SITE_PACKAGES":
                                        authority = (
                                            "SITE_PYTEST_REWRITE"
                                            if rewrite
                                            else "SITE_DISTRIBUTION_NORMAL"
                                        )
                                    else:
                                        authority = (
                                            "REPOSITORY_PYTEST_REWRITE"
                                            if rewrite
                                            else "REPOSITORY_NORMAL"
                                        )
                                    classification_fields = {}
                                elif (
                                    role == "WHOLE_REPOSITORY" and source_path in audit_only_sources
                                ):
                                    authority = "REPOSITORY_POST_W04_CACHE_AUDIT_ONLY"
                                    source_authority = None
                                    classification_fields = {
                                        "authority_scope": "AUDIT_ONLY_ZERO_READ_USE",
                                        "denial_policy": "POST_W04_SOURCE_CACHE_DENIED_ZERO_READ",
                                    }
                                else:
                                    raise RuntimeControlError(
                                        "PYC lacks stable source or exact inert-orphan authority: "
                                        f"{role}:{relative}->{source_path}"
                                    )
                            else:
                                foreign_match = foreign_pytest.fullmatch(name)
                                if foreign_match is None:
                                    foreign_match = foreign_normal.fullmatch(name)
                                if (
                                    foreign_match is None
                                    or foreign_match.group("tag") == "cpython-312"
                                ):
                                    raise RuntimeControlError("PYC filename grammar differs")
                                source_path = (
                                    (path.parent.parent / f"{foreign_match.group('stem')}.py")
                                    .relative_to(traversal_root)
                                    .as_posix()
                                )
                                if role == "WHOLE_REPOSITORY" and source_path == foreign_source:
                                    raise RuntimeControlError("PYC filename grammar differs")
                                authority = (
                                    "SITE_FOREIGN_CACHE_TAG_AUDIT_ONLY"
                                    if role == "SELECTED_SITE_PACKAGES"
                                    else "REPOSITORY_FOREIGN_CACHE_TAG_AUDIT_ONLY"
                                )
                                source_authority = None
                                classification_fields = {
                                    "authority_scope": "AUDIT_ONLY_ZERO_READ_USE",
                                    "denial_policy": "FOREIGN_INTERPRETER_TAG_DENIED_ZERO_READ",
                                    "foreign_cache_tag": foreign_match.group("tag"),
                                }
                row: dict[str, object] = {
                    "authority_class": authority,
                    "entry_kind": "PYC",
                    "mode": 0o644,
                    "path": relative,
                    "role": role,
                    "device": metadata.st_dev,
                    "inode": metadata.st_ino,
                    "mtime_ns": metadata.st_mtime_ns,
                    "ctime_ns": metadata.st_ctime_ns,
                    "size_bytes": metadata.st_size,
                    "source_path": source_path,
                    "source_authority": source_authority,
                }
                row.update(classification_fields)
                inventory.append(row)
    if seen_foreign_paths != set(foreign_by_path):
        raise RuntimeControlError("foreign-tag denied PYC path is missing")
    inventory.sort(key=_canonical_json_bytes)
    return tuple(inventory)


def _independent_pyc_security_projection(
    snapshot: tuple[dict[str, object], ...],
) -> dict[str, object]:
    """Project portable cache security facts without sharing child implementation."""

    protected: list[dict[str, object]] = []
    keys = (
        "authority_class",
        "denial_policy",
        "entry_kind",
        "foreign_cache_tag",
        "mode",
        "path",
        "role",
        "size_bytes",
        "source_authority",
        "source_authority_required",
        "source_path",
    )
    for row in snapshot:
        if row.get("authority_class") == "REPOSITORY_FOREIGN_CACHE_TAG_DENIED":
            protected.append({key: row.get(key) for key in keys})
    protected.sort(key=_canonical_json_bytes)
    return {
        "algorithm": "w10-pyc-portable-security-projection-v1",
        "audit_only_authority_classes": (
            "REPOSITORY_FOREIGN_CACHE_TAG_AUDIT_ONLY",
            "REPOSITORY_POST_W04_CACHE_AUDIT_ONLY",
            "REPOSITORY_RETIRED_POST_W04_CACHE_AUDIT_ONLY",
            "SITE_FOREIGN_CACHE_TAG_AUDIT_ONLY",
        ),
        "protected_denials": tuple(protected),
        "raw_inventory_authority": "AUDIT_ONLY_ZERO_READ_USE",
        "unsafe_metadata_policy": "FAIL_CLOSED_BEFORE_PROJECTION",
    }


def _independent_stdlib_rows() -> tuple[dict[str, object], ...]:
    stdlib = Path(os.__file__).resolve().parent
    rows: list[dict[str, object]] = []
    for directory, names, files in os.walk(stdlib, topdown=True, followlinks=False):
        names[:] = sorted(
            name
            for name in names
            if name not in {"__pycache__", "site-packages"}
            and not Path(directory, name).is_symlink()
        )
        for name in sorted(files):
            path = Path(directory, name)
            metadata = os.stat(path, follow_symlinks=False)
            if stat.S_ISLNK(metadata.st_mode):
                raise RuntimeControlError("retained stdlib contains a file symlink")
            if not stat.S_ISREG(metadata.st_mode) or name.lower().endswith((".pyc", ".pyo")):
                continue
            mode = stat.S_IMODE(metadata.st_mode)
            if mode not in {0o644, 0o755} or mode & 0o022:
                raise RuntimeControlError("retained stdlib has an unsafe writable mode")
            raw = _absolute_regular(path, mode=mode)
            rows.append(
                {
                    "mode": mode,
                    "path": path.relative_to(stdlib).as_posix(),
                    "sha256": _sha256(raw),
                    "size_bytes": len(raw),
                }
            )
    if len(rows) != 748:
        raise RuntimeControlError("retained complete stdlib cardinality differs")
    return tuple(rows)


def _independent_interpreter(root: Path) -> dict[str, object]:
    physical = Path(cast(str, getattr(sys, "_base_executable")))
    raw = _absolute_regular(physical, mode=0o755)
    if (
        len(raw) != 49_968
        or _sha256(raw) != "cf450e6bc0b00adecd12b7b13024de7000c7350801addc802bd3b45782104e79"
    ):
        raise RuntimeControlError("retained physical interpreter differs")
    bin_root = root / ".venv/bin"
    symlink_census = sorted(
        entry.name
        for entry in os.scandir(bin_root)
        if stat.S_ISLNK(entry.stat(follow_symlinks=False).st_mode)
    )
    if symlink_census != ["python", "python3", "python3.12"]:
        raise RuntimeControlError("retained exact three-alias census differs")
    identities: set[tuple[int, int]] = set()
    aliases = []
    for name in ("python", "python3", "python3.12"):
        alias = root / ".venv/bin" / name
        metadata = os.lstat(alias)
        identity = (metadata.st_dev, metadata.st_ino)
        if (
            not stat.S_ISLNK(metadata.st_mode)
            or stat.S_IMODE(metadata.st_mode) != 0o755
            or metadata.st_nlink != 1
            or identity in identities
        ):
            raise RuntimeControlError("retained interpreter alias lstat topology differs")
        identities.add(identity)
        target = os.readlink(alias)
        if (name == "python" and target != os.fspath(physical)) or (
            name != "python" and target != "python"
        ):
            raise RuntimeControlError("retained interpreter alias chain differs")
        if alias.resolve(strict=True) != physical.resolve(strict=True):
            raise RuntimeControlError("retained interpreter aliases diverge")
        aliases.append(
            {
                "alias": name,
                "raw_target_role": "<W04_PYTHON_PHYSICAL_EXECUTABLE>"
                if name == "python"
                else "python",
                "resolution_hops": 1 if name == "python" else 2,
            }
        )
    suffixes = tuple(importlib.machinery.EXTENSION_SUFFIXES)
    if (
        sys.implementation.name != "cpython"
        or sys.version != "3.12.12 (main, Dec 17 2025, 21:07:08) [Clang 21.1.4 ]"
        or sys.platform != "darwin"
        or os.uname().machine != "arm64"
        or sys.implementation.cache_tag != "cpython-312"
        or sysconfig.get_config_var("SOABI") != "cpython-312-darwin"
        or suffixes != (".cpython-312-darwin.so", ".abi3.so", ".so")
    ):
        raise RuntimeControlError("retained interpreter implementation/ABI differs")
    library_name = sysconfig.get_config_var("LDLIBRARY")
    library_root = sysconfig.get_config_var("LIBDIR")
    if type(library_name) is not str or type(library_root) is not str:
        raise RuntimeControlError("retained libpython image is absent")
    path = Path(library_root) / library_name
    library_raw = _absolute_regular(path, mode=0o755)
    library_digest = "e8b85a555061f39891e08783d18bc56f3444fefdde2a5f2ffcdb6b37dd217460"
    if (
        library_name != "libpython3.12.dylib"
        or len(library_raw) != 17_864_576
        or _sha256(library_raw) != library_digest
        or sysconfig.get_config_var("SHLIB_SUFFIX") != ".so"
        or sysconfig.get_config_var("MULTIARCH") != "darwin"
        or sysconfig.get_config_var("MACHDEP") != "darwin"
    ):
        raise RuntimeControlError("retained libpython/loader configuration differs")
    loader_raw = _absolute_regular(Path("/usr/lib/dyld"), mode=0o755)
    if (
        len(loader_raw) != 2_374_000
        or _sha256(loader_raw) != "6da2d109f72330d031450f3c0ebea14bfc10f42f844a958858e16a4092c38f12"
    ):
        raise RuntimeControlError("retained Darwin dynamic loader differs")
    library = {
        "mode": 0o755,
        "role": "W04_LIBPYTHON",
        "sha256": _sha256(library_raw),
        "size_bytes": len(library_raw),
    }
    return {
        "alias_policy": "w04-venv-wrapper-interpreter-alias-v2",
        "aliases": aliases,
        "abi_flags": sys.abiflags,
        "cache_tag": sys.implementation.cache_tag,
        "extension_suffixes": list(suffixes),
        "full_version": sys.version,
        "implementation": "cpython",
        "launch_alias_observation": "python3",
        "libpython": library,
        "loader": {
            "mode": 0o755,
            "role": "W04_DARWIN_DYNAMIC_LOADER",
            "sha256": _sha256(loader_raw),
            "size_bytes": len(loader_raw),
        },
        "loader_configuration": {
            "ldlibrary": "libpython3.12.dylib",
            "machdep": "darwin",
            "multiarch": "darwin",
            "shlib_suffix": ".so",
        },
        "machine": "arm64",
        "physical_sha256": _sha256(raw),
        "physical_size_bytes": len(raw),
        "python_version": "3.12.12",
        "required_aliases": ["python", "python3", "python3.12"],
        "soabi": "cpython-312-darwin",
        "sys_platform": "darwin",
    }


def _independent_uv(root: Path) -> dict[str, object]:
    logical = Path("/opt/homebrew/bin/uv")
    if not logical.is_symlink() or os.readlink(logical) != "../Cellar/uv/0.9.21/bin/uv":
        raise RuntimeControlError("retained logical uv link differs")
    raw = _absolute_regular(Path("/opt/homebrew/Cellar/uv/0.9.21/bin/uv"), mode=0o555)
    digest = "4f0c0c002bb4702c1bd6792edc15f7ae3948b5f19509c8d73cd5c9a26298097f"
    version = "uv 0.9.21 (Homebrew 2025-12-30)"
    if len(raw) != 41_617_552 or _sha256(raw) != digest:
        raise RuntimeControlError("retained physical uv bytes differ")
    observed = subprocess.run(  # nosec B603
        ("uv", "--version"),
        cwd=root,
        env={
            "LANG": "C",
            "LC_ALL": "C",
            "PATH": "/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin",
            "UV": "/opt/homebrew/bin/uv",
        },
        stdin=subprocess.DEVNULL,
        capture_output=True,
        check=False,
        timeout=10,
    )
    if observed.returncode or observed.stdout != (version + "\n").encode() or observed.stderr:
        raise RuntimeControlError("retained normal logical uv observation differs")
    return {
        "link_policy": "w04-uv-logical-one-hop-relative-link-v1",
        "physical_sha256": digest,
        "physical_size_bytes": len(raw),
        "uv_version": version,
        "version_observed_through_literal_" + "token": True,
    }


def _independent_extracted_authority(
    root: Path, wheels: tuple[dict[str, object], ...]
) -> tuple[tuple[dict[str, object], ...], dict[str, dict[str, object]]]:
    cache = Path(os.environ.get("UV_CACHE_DIR", os.fspath(Path.home() / ".cache/uv"))).absolute()
    archive = cache / "archive-v0"
    archive_metadata = os.lstat(archive)
    if not stat.S_ISDIR(archive_metadata.st_mode) or stat.S_ISLNK(archive_metadata.st_mode):
        raise RuntimeControlError("retained archive-v0 root is not one physical directory")
    site = root / ".venv/lib/python3.12/site-packages"
    rows: list[dict[str, object]] = []
    mapped_destinations: dict[str, dict[str, object]] = {}
    extracted_identities: set[tuple[int, int]] = set()
    for wheel in wheels:
        filename, version, name = (
            cast(str, wheel["filename"]),
            cast(str, wheel["version"]),
            cast(str, wheel["name"]),
        )
        marker = f"-{version}-"
        key = filename[filename.index(marker) + 1 : -4]
        association = cache / "wheels-v5" / "pypi" / name / key
        association_metadata = os.lstat(association)
        if not stat.S_ISLNK(association_metadata.st_mode) or association_metadata.st_nlink != 1:
            raise RuntimeControlError("retained selected-wheel cache association differs")
        raw_target = os.readlink(association)
        if not raw_target or "\x00" in raw_target:
            raise RuntimeControlError("retained selected-wheel target is empty or malformed")
        raw_path = Path(raw_target)
        extracted = (
            raw_path if raw_path.is_absolute() else association.parent / raw_path
        ).absolute()
        extracted_metadata = os.lstat(extracted)
        if (
            not extracted.is_relative_to(archive)
            or not stat.S_ISDIR(extracted_metadata.st_mode)
            or stat.S_ISLNK(extracted_metadata.st_mode)
        ):
            raise RuntimeControlError("retained selected-wheel extraction escapes archive")
        extracted_identity = (extracted_metadata.st_dev, extracted_metadata.st_ino)
        if extracted_identity in extracted_identities:
            raise RuntimeControlError("retained selected wheels share one extracted target")
        extracted_identities.add(extracted_identity)
        record = extracted / f"{name.replace('-', '_')}-{version}.dist-info/RECORD"
        declarations = list(
            csv.reader(
                _absolute_regular(record, mode=stat.S_IMODE(record.stat().st_mode))
                .decode()
                .splitlines()
            )
        )
        declaration_by_path: dict[str, list[str]] = {}
        for declaration in declarations:
            if len(declaration) != 3:
                raise RuntimeControlError("retained extracted RECORD row shape differs")
            relative = declaration[0]
            parsed = Path(relative)
            if (
                parsed.is_absolute()
                or "\\" in relative
                or ".." in parsed.parts
                or "." in parsed.parts
                or relative in declaration_by_path
            ):
                raise RuntimeControlError("retained extracted RECORD path differs")
            declaration_by_path[relative] = declaration
        tree: list[dict[str, object]] = []
        physical: set[str] = set()
        for directory, directory_names, files in os.walk(
            extracted, topdown=True, followlinks=False
        ):
            if any(Path(directory, name).is_symlink() for name in directory_names):
                raise RuntimeControlError("retained extracted tree contains a directory symlink")
            directory_names.sort()
            for file_name in sorted(files):
                path = Path(directory, file_name)
                metadata = os.stat(path, follow_symlinks=False)
                raw = _absolute_regular(path, mode=stat.S_IMODE(metadata.st_mode))
                relative = path.relative_to(extracted).as_posix()
                physical.add(relative)
                tree.append(
                    {
                        "mode": stat.S_IMODE(metadata.st_mode),
                        "path": relative,
                        "sha256": _sha256(raw),
                        "size_bytes": len(raw),
                    }
                )
        if physical != set(declaration_by_path):
            raise RuntimeControlError("retained extracted wheel tree differs from RECORD")
        record_relative = record.relative_to(extracted).as_posix()
        for tree_row in tree:
            relative = cast(str, tree_row["path"])
            digest_cell, size_cell = declaration_by_path[relative][1:]
            if relative == record_relative:
                if digest_cell or size_cell:
                    raise RuntimeControlError("retained extracted RECORD self row differs")
                continue
            encoded = (
                base64.urlsafe_b64encode(bytes.fromhex(cast(str, tree_row["sha256"])))
                .decode()
                .rstrip("=")
            )
            if digest_cell != f"sha256={encoded}" or size_cell != str(tree_row["size_bytes"]):
                raise RuntimeControlError("retained extracted RECORD declaration differs")
            parts = Path(relative).parts
            data_index = next(
                (index for index, part in enumerate(parts) if part.endswith(".data")), None
            )
            if data_index is None:
                installed_path = site / relative
                scheme = "root"
            else:
                if data_index != 0 or len(parts) < 3:
                    raise RuntimeControlError("retained wheel data-scheme path shape differs")
                scheme, tail = parts[data_index + 1], parts[data_index + 2 :]
                if scheme in {"purelib", "platlib"}:
                    installed_path = site.joinpath(*tail)
                elif scheme == "scripts":
                    installed_path = root / ".venv/bin" / Path(*tail)
                elif scheme == "headers":
                    installed_path = root / ".venv/include/site/python3.12" / name / Path(*tail)
                elif scheme == "data":
                    installed_path = root / ".venv" / Path(*tail)
                else:
                    raise RuntimeControlError("retained wheel PEP 427 scheme differs")
            if not installed_path.is_relative_to(root / ".venv"):
                raise RuntimeControlError("retained wheel mapping escapes the environment")
            destination = installed_path.relative_to(root / ".venv").as_posix()
            mapped = {
                "mode": tree_row["mode"],
                "owner": name,
                "record_path": relative,
                "scheme": scheme,
                "sha256": tree_row["sha256"],
                "size_bytes": tree_row["size_bytes"],
            }
            if destination in mapped_destinations and mapped_destinations[destination] != mapped:
                raise RuntimeControlError("retained wheel mapping collides or overwrites")
            mapped_destinations[destination] = mapped
            installed_raw = _absolute_regular(
                installed_path, mode=stat.S_IMODE(installed_path.stat().st_mode)
            )
            if _sha256(installed_raw) != tree_row["sha256"]:
                raise RuntimeControlError("retained extracted-to-installed mapping differs")
        rows.append(
            {
                "association_policy": "one-symlink-contained-archive-v0",
                "cache_key": key,
                "name": name,
                "tree_digest": _sha256_json(tree),
                "tree_row_count": len(tree),
                "version": version,
                "wheel": wheel,
            }
        )
    return tuple(rows), mapped_destinations


def _independent_extracted_rows(
    root: Path, wheels: tuple[dict[str, object], ...]
) -> tuple[dict[str, object], ...]:
    """Return stable extracted rows while keeping mapping evidence operational."""

    rows, _mapping = _independent_extracted_authority(root, wheels)
    return rows


def _admission_authority_with_pyc(
    project_root: Path,
) -> tuple[
    str,
    dict[str, object],
    tuple[int, ...],
    tuple[dict[str, object], ...],
]:
    """Separately reconstruct all retained child authorities without loading child code."""

    repository = _independent_repository_rows(project_root)
    lock_inputs: dict[str, object] = {
        "pyproject_sha256": _sha256(_guard_read_relative(project_root, "pyproject.toml")),
        "uv_lock_sha256": _sha256(
            _guard_read_relative(project_root, "uv.lock", max_bytes=128 * 1024 * 1024)
        ),
    }
    if lock_inputs != {"pyproject_sha256": PYPROJECT_SHA256, "uv_lock_sha256": UV_LOCK_SHA256}:
        raise RuntimeControlError("retained lock input bytes differ")
    preliminary = _independent_lock_rows(project_root)
    installed = _independent_installed_rows(project_root, preliminary)
    bootstrap, editable_detail = _independent_site_editable_authority(
        project_root, installed, repository, lock_inputs
    )
    stable_installed = _independent_stable_records(project_root, installed)
    selector, closure, wheels = _independent_selector_closure_wheels(
        project_root, preliminary, installed
    )
    extracted, mapped_destinations = _independent_extracted_authority(project_root, wheels)
    _independent_validate_installed_mapping(project_root, installed, mapped_destinations)
    executables = _independent_executable_rows(project_root, installed)
    resources = tuple(
        _authority_file_row(project_root, path, mode=0o600 if index == 16 else 0o644)
        for index, path in enumerate(_LOCAL_RESOURCE_PATHS)
    )
    stdlib = _independent_stdlib_rows()
    interpreter = _independent_interpreter(project_root)
    uv = _independent_uv(project_root)
    pyc = _independent_pyc_detail(project_root, installed, repository, bootstrap)
    pyc_before = _independent_pyc_inventory(project_root, pyc)
    admission_environment = dict(_STATIC_CHILD_ENVIRONMENT)
    admission_environment["UV_RUN_RECURSION_DEPTH"] = "1"
    admission_tokens = dict(_NORMALIZED_ENVIRONMENT_TOKENS)
    admission_tokens["PYTHONPYCACHEPREFIX"] = "<ADMISSION_PREFIX>"
    launcher_row = next(row for row in repository if row["path"] == "scripts/launch_wyscout_v5.py")
    details: dict[str, object] = {
        "child_result_contract_digest": {
            "frame_magic": "W04CRSLT",
            "frame_version": 1,
            "payload_schema": CHILD_RESULT_SCHEMA_VERSION,
            "roles": ["PRE_BUILD_ADMISSION", "POST_BUILD_ID_REBUILD"],
            "runtime_subset": {
                "algorithm": RUNTIME_SUBSET_ALGORITHM,
                "final_recheck_schema": FINAL_RECHECK_SCHEMA_VERSION,
                "observation_fields": list(RUNTIME_OBSERVATION_FIELDS),
                "observation_kinds": list(RUNTIME_OBSERVATION_KINDS),
            },
        },
        "editable_root_digest": editable_detail,
        "environment_values_digest": {
            "algorithm": "w04-child-environment-input-v2",
            "literal_environment": admission_environment,
            "normalized_tokens": admission_tokens,
            "required_absent": REQUIRED_ABSENT_ENVIRONMENT,
        },
        "executable_census_digest": {
            "algorithm": "w04-installed-executable-census-v3",
            "rows": executables,
        },
        "extracted_runtime_digest": {
            "algorithm": "w04-verified-cache-extracted-pep427-v1",
            "rows": extracted,
        },
        "installed_record_runtime_digest": {
            "algorithm": "w04-installed-record-runtime-v1",
            "ownership_policy": "singular-record-owner-complete-site-closure-v1",
            "rows": stable_installed,
            "runtime_subset_policy": RUNTIME_SUBSET_POLICY,
        },
        "interpreter_digest": interpreter,
        "local_launcher_control_digest": {
            "algorithm": "w04-local-control-bootstrap-v4",
            "launcher": launcher_row,
            "ordered_argv": list(ADMISSION_ARGV),
            "source_descriptor_policy": "w04-inherited-source-fd-v1",
            "uv_authority": uv,
        },
        "local_resource_digest": {
            "algorithm": _LOCAL_RESOURCE_DIGEST_ALGORITHM,
            "rows": resources,
        },
        "lock_inputs_digest": lock_inputs,
        "process_launch_contract_digest": {
            "admission_argv": list(ADMISSION_ARGV),
            "child_process_observation_policy": "operational-build-excluded-closed-v1",
            "child_roles": ["PRE_BUILD_ADMISSION", "POST_BUILD_ID_REBUILD"],
            "child_input_schema": CHILD_INPUT_SCHEMA_VERSION,
            "projection_schema": "w04-wyscout-pre-build-projection-v1",
            "rebuild_argv": list(REBUILD_ARGV),
        },
        "pyc_policy_source_map_digest": pyc,
        "selected_lock_closure_digest": {
            "algorithm": "w04-selected-all-groups-lock-closure-v1",
            "groups": [
                "data",
                "e2e",
                "lint-type",
                "model",
                "orchestration",
                "runtime",
                "security",
                "test",
            ],
            "rows": closure,
        },
        "selector": selector,
        "selector_bootstrap_digest": {
            "algorithm": "w04-packaging-tag-bootstrap-v1",
            "packaging_record": next(row for row in installed if row["name"] == "packaging"),
            "selector": selector,
        },
        "stdlib_digest": {"algorithm": "w04-stdlib-exact-sources-v1", "rows": stdlib},
        "uv_physical_sha256": "4f0c0c002bb4702c1bd6792edc15f7ae3948b5f19509c8d73cd5c9a26298097f",
        "uv_version": "uv 0.9.21 (Homebrew 2025-12-30)",
        "venv_bootstrap_digest": {"algorithm": "w04-uv-venv-bootstrap-deny-v1", "rows": bootstrap},
        "wheel_declaration_digest": {
            "algorithm": "w04-complete-wheel-declaration-v1",
            "rows": wheels,
        },
    }
    components: dict[str, object] = {}
    counts: list[int] = []
    for key in COMPONENT_KEYS:
        detail = details[key]
        if key in {"selector", "uv_physical_sha256", "uv_version"}:
            components[key] = detail
        else:
            components[key] = _sha256_json(detail)
        if isinstance(detail, dict) and isinstance(detail.get("rows"), tuple):
            counts.append(max(1, len(cast(tuple[object, ...], detail["rows"]))))
        else:
            counts.append(1)
    repository_digest = _sha256_json(
        {"algorithm": "w04-explicit-repository-code-manifest-v1", "rows": repository}
    )
    pyc_after = _independent_pyc_inventory(project_root, pyc)
    if _independent_pyc_security_projection(pyc_after) != _independent_pyc_security_projection(
        pyc_before
    ):
        raise RuntimeControlError("portable PYC security projection changed")
    return repository_digest, components, tuple(counts), pyc_before


def _admission_authority(project_root: Path) -> tuple[str, dict[str, object], tuple[int, ...]]:
    repository, components, counts, _pyc = _admission_authority_with_pyc(project_root)
    return repository, components, counts


def _entrypoint_source(project_root: Path, relative_path: str) -> _GuardedSource:
    raw = _guard_read_relative(project_root, relative_path, max_bytes=MAX_FRAME_PAYLOAD_BYTES)
    root_fd = os.open(project_root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    descriptors = [root_fd]
    try:
        current = root_fd
        parts = relative_path.split("/")
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=current)
            descriptors.append(child)
            current = child
        descriptor = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=current)
    finally:
        for inherited in reversed(descriptors):
            os.close(inherited)
    metadata = os.fstat(descriptor)
    if (
        not stat.S_ISREG(metadata.st_mode)
        or stat.S_IMODE(metadata.st_mode) != 0o644
        or metadata.st_nlink != 1
        or metadata.st_size != len(raw)
    ):
        os.close(descriptor)
        raise RuntimeControlError("entrypoint descriptor authority differs")
    if os.lseek(descriptor, 0, os.SEEK_CUR) != 0:
        os.close(descriptor)
        raise RuntimeControlError("entrypoint descriptor offset is not zero")
    os.set_inheritable(descriptor, True)
    return _GuardedSource(
        descriptor=descriptor,
        relative_path=relative_path,
        sha256=_sha256(raw),
        size_bytes=len(raw),
        device=metadata.st_dev,
        inode=metadata.st_ino,
    )


def _normal_environment_object(environment: dict[str, str], role: str) -> dict[str, object]:
    normalized = dict(environment)
    for key, token in _NORMALIZED_ENVIRONMENT_TOKENS.items():
        if key not in normalized:
            raise RuntimeControlError(f"closed child environment lacks {key}")
        normalized[key] = token
    normalized["PYTHONPYCACHEPREFIX"] = (
        "<ADMISSION_PREFIX>" if role == "PRE_BUILD_ADMISSION" else "<REBUILD_PREFIX>"
    )
    return {
        "algorithm": "w04-child-environment-input-v2",
        "excluded_until_insertion": ["W04_CHILD_INPUT_B64"],
        "present": {key: normalized[key] for key in sorted(normalized)},
        "required_absent": list(REQUIRED_ABSENT_ENVIRONMENT),
    }


def _closed_child_environment(
    *,
    project_root: Path,
    pycache_prefix: Path,
    role: str,
    source_fd: int,
    result_fd: int,
    nonce: str,
) -> dict[str, str]:
    environment = dict(_STATIC_CHILD_ENVIRONMENT)
    environment.update(
        {
            "HOME": "/Users/adrian",
            "PATH": "/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin",
            "PYTHONPYCACHEPREFIX": os.fspath(pycache_prefix),
            "TMPDIR": "/var/folders/8r/chc2bb390r9cw7s2m65b21h80000gn/T/",
            "UV": "/opt/homebrew/bin/uv",
            "UV_CACHE_DIR": "/Users/adrian/.cache/uv",
            "VIRTUAL_ENV": os.fspath(project_root / ".venv"),
            "W04_CHILD_ROLE": role,
            "W04_ENTRYPOINT_SOURCE_FD": str(source_fd),
            "W04_RESULT_FD": str(result_fd),
            "W04_RESULT_NONCE": nonce,
            "__CF_USER_TEXT_ENCODING": "0x1F5:0:2",
        }
    )
    return environment


def _encoded_child_input(value: dict[str, object]) -> str:
    raw = _canonical_json_bytes(value)
    if not 1 <= len(raw) <= 262_144 or _load_canonical_json(raw) != value:
        raise RuntimeControlError("child input envelope is outside the canonical bound")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _create_empty_prefix(root: Path, role: str, run_id: str, build_id: str | None) -> Path:
    if not root.is_absolute():
        raise RuntimeControlError("pycache staging root must be absolute")
    metadata = os.stat(root, follow_symlinks=False)
    if not stat.S_ISDIR(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
        raise RuntimeControlError("pycache staging root must be a real directory")
    if stat.S_IMODE(metadata.st_mode) != 0o700:
        raise RuntimeControlError("pycache staging root must have mode 0700")
    if role == "PRE_BUILD_ADMISSION":
        stable_parent_parts = ("admission",)
        selected_parts = (f"admission_run_id={run_id}", "runtime-pycache")
    else:
        if build_id is None or SHA256_RE.fullmatch(build_id) is None:
            raise RuntimeControlError("rebuild prefix requires the completed build ID")
        stable_parent_parts = (build_id,)
        selected_parts = (run_id, "runtime-pycache")
    current = root
    for part in stable_parent_parts:
        current = current / part
        try:
            os.mkdir(current, 0o700)
        except FileExistsError:
            existing = os.stat(current, follow_symlinks=False)
            if (
                not stat.S_ISDIR(existing.st_mode)
                or stat.S_ISLNK(existing.st_mode)
                or stat.S_IMODE(existing.st_mode) != 0o700
            ):
                raise RuntimeControlError("stable prefix parent is unsafe") from None
    selected_root = current / selected_parts[0]
    try:
        os.mkdir(selected_root, 0o700)
    except FileExistsError as error:
        raise RuntimeControlError("selected child run prefix already exists") from error
    current = selected_root
    for part in selected_parts[1:]:
        current = current / part
        os.mkdir(current, 0o700)
    leaf = current
    if tuple(os.scandir(leaf)):
        raise RuntimeControlError("selected child prefix is not empty")
    return leaf


def _ensure_mode_0700_directory(path: Path) -> None:
    try:
        os.mkdir(path, 0o700)
    except FileExistsError:
        pass
    metadata = os.stat(path, follow_symlinks=False)
    if (
        not stat.S_ISDIR(metadata.st_mode)
        or stat.S_ISLNK(metadata.st_mode)
        or stat.S_IMODE(metadata.st_mode) != 0o700
    ):
        raise RuntimeControlError("runtime-control directory is unsafe")


def _resolve_child_executable(argv0: str, environment: dict[str, str]) -> str:
    if "/" in argv0:
        candidate = Path(argv0)
        return os.fspath(candidate if candidate.is_absolute() else candidate.absolute())
    for directory in environment["PATH"].split(":"):
        candidate = Path(directory) / argv0
        try:
            metadata = os.stat(candidate, follow_symlinks=True)
        except FileNotFoundError:
            continue
        if stat.S_ISREG(metadata.st_mode) and os.access(candidate, os.X_OK):
            return os.fspath(candidate)
    raise ChildProcessError("child executable is not resolvable from the closed PATH")


def _validate_child_process_observation(
    observation: dict[str, object],
    *,
    expected_role: str,
    expected_facts: dict[str, object] | None = None,
) -> None:
    if tuple(observation) != CHILD_PROCESS_OBSERVATION_FIELDS:
        raise RuntimeControlError("child process observation roster/order differs")
    if expected_role not in {"PRE_BUILD_ADMISSION", "POST_BUILD_ID_REBUILD"}:
        raise RuntimeControlError("child process observation expected role is unknown")
    if observation["child_role"] != expected_role:
        raise RuntimeControlError("child process observation role differs")
    expected_argv = ADMISSION_ARGV if expected_role == "PRE_BUILD_ADMISSION" else REBUILD_ARGV
    expected_kind = (
        "CODE_ENVIRONMENT_MANIFEST"
        if expected_role == "PRE_BUILD_ADMISSION"
        else "REBUILD_COMPLETION"
    )
    for field in (
        "cross_field_binding",
        "diagnostics_empty",
        "frame_eof",
        "in_place_pyc_unchanged",
        "not_timed_out",
        "prefix_empty_after",
        "prefix_empty_before",
        "prefix_identity_unchanged",
        "result_descriptor_inheritable",
        "result_descriptor_parent_closed",
        "source_descriptor_checkpoint",
        "zero_in_place_pyc_reads",
    ):
        if observation[field] is not True:
            raise RuntimeControlError(f"child process observation boolean differs: {field}")
    if (
        observation["exit_code"] != 0
        or observation["argv"] != list(expected_argv)
        or observation["argv_sha256"] != _sha256_json(list(expected_argv))
        or observation["payload_kind"] != expected_kind
        or observation["frame_count"] != 1
        or observation["frame_magic"] != "W04CRSLT"
        or observation["frame_version"] != 1
        or observation["child_input_schema_version"] != CHILD_INPUT_SCHEMA_VERSION
        or observation["result_schema_version"] != CHILD_RESULT_SCHEMA_VERSION
        or observation["stdout_size_bytes"] != 0
        or observation["stderr_size_bytes"] != 0
        or observation["stdout_sha256"] != _sha256(b"")
        or observation["stderr_sha256"] != _sha256(b"")
    ):
        raise RuntimeControlError("child process observation fixed success binding differs")
    if (
        observation["initial_uv_value"] != "/opt/homebrew/bin/uv"
        or observation["uv_path_resolution"] != "/opt/homebrew/bin/uv"
        or observation["final_uv_value"] != "/opt/homebrew/bin/uv"
    ):
        raise RuntimeControlError("child process UV observation differs")
    for field in ("process_id", "result_descriptor_number", "timeout_milliseconds"):
        if type(observation[field]) is not int or cast(int, observation[field]) <= 0:
            raise RuntimeControlError(f"child process observation integer differs: {field}")
    for field in (
        "frame_payload_sha256",
        "nonce",
        "transport_environment_sha256",
    ):
        if (
            type(observation[field]) is not str
            or SHA256_RE.fullmatch(cast(str, observation[field])) is None
        ):
            raise RuntimeControlError(f"child process observation SHA-256 differs: {field}")
    if (
        type(observation["frame_payload_size_bytes"]) is not int
        or observation["frame_payload_size_bytes"] <= 0
        or type(observation["prefix_absolute_path"]) is not str
        or not Path(observation["prefix_absolute_path"]).is_absolute()
        or type(observation["prefix_relative_path"]) is not str
    ):
        raise RuntimeControlError("child process observation size/prefix differs")
    prefix_relative = observation["prefix_relative_path"]
    if (
        not is_normalized("NFC", prefix_relative)
        or Path(prefix_relative).is_absolute()
        or "\\" in prefix_relative
        or prefix_relative.endswith("/")
        or any(part in {"", ".", ".."} for part in prefix_relative.split("/"))
    ):
        raise RuntimeControlError("child process relative prefix is unsafe")
    before = observation["prefix_identity_before"]
    after = observation["prefix_identity_after"]
    identity_fields = ("device", "inode", "link_count", "mode")
    if (
        type(before) is not dict
        or type(after) is not dict
        or tuple(cast(dict[str, object], before)) != identity_fields
        or tuple(cast(dict[str, object], after)) != identity_fields
        or before != after
        or any(type(cast(dict[str, object], before)[field]) is not int for field in identity_fields)
        or cast(dict[str, object], before)["link_count"] != 2
        or cast(dict[str, object], before)["mode"] != 0o700
    ):
        raise RuntimeControlError("child process prefix identity binding differs")
    entrypoint = observation["entrypoint_source"]
    if type(entrypoint) is not dict:
        raise RuntimeControlError("child process entrypoint observation is not an object")
    entry = cast(dict[str, object], entrypoint)
    if (
        tuple(entry) != ENTRYPOINT_OBSERVATION_FIELDS
        or entry.get("role") != expected_role
        or entry.get("relative_path") != expected_argv[-1]
        or entry.get("descriptor_inheritable") is not True
        or entry.get("descriptor_cloexec") is not False
        or entry.get("source_eof") is not True
        or entry.get("offset_before") != 0
        or entry.get("offset_after") != 0
        or type(entry.get("descriptor_number")) is not int
        or cast(int, entry["descriptor_number"]) <= 0
        or type(entry.get("device")) is not int
        or cast(int, entry["device"]) <= 0
        or type(entry.get("inode")) is not int
        or cast(int, entry["inode"]) <= 0
        or entry.get("link_count") != 1
        or entry.get("mode") != 0o644
        or type(entry.get("size_bytes")) is not int
        or cast(int, entry["size_bytes"]) <= 0
        or type(entry.get("sha256")) is not str
        or SHA256_RE.fullmatch(cast(str, entry["sha256"])) is None
        or entry.get("descriptor_number") == observation["result_descriptor_number"]
    ):
        raise RuntimeControlError("child process entrypoint cross-field binding differs")
    if expected_facts is not None:
        for field, expected in expected_facts.items():
            if field not in observation or observation[field] != expected:
                raise RuntimeControlError(f"child process retained fact differs: {field}")


def _decode_child_process_observation(
    raw: bytes, *, expected_role: str, expected_facts: dict[str, object] | None = None
) -> dict[str, object]:
    if type(raw) is not bytes or not 1 <= len(raw) <= 262_144:
        raise RuntimeControlError("child process observation bytes are malformed")
    value = _load_canonical_json(raw)
    if type(value) is not dict or _canonical_json_bytes(value) != raw:
        raise RuntimeControlError("child process observation is not one canonical object")
    observation = cast(dict[str, object], value)
    _validate_child_process_observation(
        observation, expected_role=expected_role, expected_facts=expected_facts
    )
    return observation


def _drain_child(
    process: subprocess.Popen[bytes], result_reader: int, *, timeout: float
) -> tuple[bytes, bytes, bytes]:
    selector = selectors.DefaultSelector()
    if process.stdout is None or process.stderr is None:
        raise ChildProcessError("child diagnostic pipes are unavailable")
    streams = {
        result_reader: ("result", None),
        process.stdout.fileno(): ("stdout", process.stdout),
        process.stderr.fileno(): ("stderr", process.stderr),
    }
    for descriptor in streams:
        os.set_blocking(descriptor, False)
        selector.register(descriptor, selectors.EVENT_READ)
    buffers = {"result": bytearray(), "stdout": bytearray(), "stderr": bytearray()}
    deadline = time.monotonic() + timeout
    try:
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                process.kill()
                process.wait()
                raise ChildProcessError("child exceeded the monotonic deadline")
            events = selector.select(min(remaining, 0.25))
            if not events and process.poll() is not None:
                events = [(key, selectors.EVENT_READ) for key in selector.get_map().values()]
            for key, _mask in events:
                label, _stream = streams[key.fd]
                try:
                    chunk = os.read(key.fd, 64 * 1024)
                except BlockingIOError:
                    continue
                if not chunk:
                    selector.unregister(key.fd)
                    continue
                buffers[label].extend(chunk)
                limit = (
                    MAX_FRAME_PAYLOAD_BYTES + FRAME_HEADER_BYTES + FRAME_DIGEST_BYTES
                    if label == "result"
                    else MAX_DIAGNOSTIC_BYTES
                )
                if len(buffers[label]) > limit:
                    process.kill()
                    process.wait()
                    raise ChildProcessError(f"child {label} channel exceeded its bound")
        status = process.wait(timeout=max(0.1, deadline - time.monotonic()))
        if status != 0:
            raise ChildProcessError(
                f"child exited {status}; stdout={bytes(buffers['stdout'])!r}; "
                f"stderr={bytes(buffers['stderr'])!r}"
            )
        return bytes(buffers["result"]), bytes(buffers["stdout"]), bytes(buffers["stderr"])
    finally:
        selector.close()


def _run_child(
    *,
    project_root: Path,
    argv: tuple[str, ...],
    role: str,
    inputs: dict[str, object],
    expected_repository_code_sha256: str,
    pycache_prefix: Path,
    timeout: float,
    retained_launcher_sha256: str | None = None,
) -> ChildExecution:
    contracts, _publication = _runtime_contracts(project_root)
    prefix_before = os.stat(pycache_prefix, follow_symlinks=False)
    prefix_identity = (
        prefix_before.st_dev,
        prefix_before.st_ino,
        prefix_before.st_mode,
        prefix_before.st_nlink,
    )
    prefix_identity_before = {
        "device": prefix_before.st_dev,
        "inode": prefix_before.st_ino,
        "link_count": prefix_before.st_nlink,
        "mode": stat.S_IMODE(prefix_before.st_mode),
    }
    prefix_empty_before = not tuple(os.scandir(pycache_prefix))
    if not prefix_empty_before:
        raise ChildProcessError("selected child pycache prefix is not initially empty")
    source = _entrypoint_source(project_root, argv[-1])
    result_reader, result_writer = os.pipe()
    nonce = secrets.token_hex(32)
    os.set_inheritable(result_writer, True)
    try:
        environment = _closed_child_environment(
            project_root=project_root,
            pycache_prefix=pycache_prefix,
            role=role,
            source_fd=source.descriptor,
            result_fd=result_writer,
            nonce=nonce,
        )
        child_python_environment = dict(environment)
        child_python_environment["UV_RUN_RECURSION_DEPTH"] = "1"
        child_python_environment["PATH"] = (
            f"{project_root}/.venv/bin:" + child_python_environment["PATH"]
        )
        base_digest = _sha256(
            _canonical_json_bytes(_normal_environment_object(child_python_environment, role))
        )
        launcher_sha256 = retained_launcher_sha256
        if launcher_sha256 is None:
            launcher_sha256 = _sha256(
                _guard_read_relative(project_root, "scripts/launch_wyscout_v5.py")
            )
        if SHA256_RE.fullmatch(launcher_sha256) is None:
            raise RuntimeControlError("retained launcher digest is malformed")
        envelope = {
            "base_environment_digest": base_digest,
            "child_role": role,
            "entrypoint_relative_path": source.relative_path,
            "entrypoint_sha256": source.sha256,
            "entrypoint_size_bytes": source.size_bytes,
            "expected_repository_code_sha256": expected_repository_code_sha256,
            "inputs": inputs,
            "launcher_sha256": launcher_sha256,
            "nonce": nonce,
            "ordered_argv": list(argv),
            "ordered_argv_sha256": _sha256(_canonical_json_bytes(list(argv))),
            "pycache_prefix_absolute": os.fspath(pycache_prefix),
            "pycache_prefix_relative": cast(
                str, inputs[next(key for key in inputs if key.endswith("prefix_relative_path"))]
            ),
            "result_descriptor_number": result_writer,
            "schema_version": CHILD_INPUT_SCHEMA_VERSION,
            "source_descriptor_number": source.descriptor,
        }
        environment["W04_CHILD_INPUT_B64"] = _encoded_child_input(envelope)
        expected_transport_environment_sha256 = _sha256(
            _canonical_json_bytes(
                {
                    **child_python_environment,
                    "W04_CHILD_INPUT_B64": environment["W04_CHILD_INPUT_B64"],
                }
            )
        )
        uv_path_resolution = _resolve_child_executable(argv[0], environment)
        if (
            environment.get("UV") != "/opt/homebrew/bin/uv"
            or uv_path_resolution != "/opt/homebrew/bin/uv"
        ):
            raise ChildProcessError("child UV observations differ before execution")
        result_descriptor_inheritable = os.get_inheritable(result_writer)
        if not result_descriptor_inheritable:
            raise ChildProcessError("child result descriptor is not inheritable")
        # The selected argv is one of the two module constants and is never caller-built.
        process = subprocess.Popen(  # noqa: S603  # nosec B603
            argv,
            cwd=project_root,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds=True,
            pass_fds=(source.descriptor, result_writer),
        )
        os.close(result_writer)
        result_writer = -1
        try:
            os.fstat(cast(int, envelope["result_descriptor_number"]))
        except OSError:
            result_descriptor_parent_closed = True
        else:
            result_descriptor_parent_closed = False
        if not result_descriptor_parent_closed:
            raise ChildProcessError("parent retained the child result descriptor")
        frame, stdout, stderr = _drain_child(process, result_reader, timeout=timeout)
        payload = decode_result_frame(frame)
        _load_canonical_json(payload)
        result = contracts.ChildResultEnvelope.model_validate_json(payload, strict=True)
        if (
            result.child_role != role
            or result.nonce != nonce
            or result.launcher_sha256 != envelope["launcher_sha256"]
            or result.child_environment_sha256 != expected_transport_environment_sha256
            or result.expected_repository_code_sha256 != expected_repository_code_sha256
            or result.entrypoint_source.descriptor_number != source.descriptor
            or result.entrypoint_source.sha256 != source.sha256
            or result.entrypoint_source.size_bytes != source.size_bytes
            or result.entrypoint_source.device != source.device
            or result.entrypoint_source.inode != source.inode
        ):
            raise ChildProcessError("child result differs from retained launch authority")
        retained = os.fstat(source.descriptor)
        if (
            retained.st_dev != source.device
            or retained.st_ino != source.inode
            or retained.st_size != source.size_bytes
            or os.lseek(source.descriptor, 0, os.SEEK_CUR) != 0
        ):
            raise ChildProcessError("retained child source descriptor changed")
        prefix_after = os.stat(pycache_prefix, follow_symlinks=False)
        prefix_identity_after = {
            "device": prefix_after.st_dev,
            "inode": prefix_after.st_ino,
            "link_count": prefix_after.st_nlink,
            "mode": stat.S_IMODE(prefix_after.st_mode),
        }
        prefix_empty_after = not tuple(os.scandir(pycache_prefix))
        if (
            prefix_after.st_dev,
            prefix_after.st_ino,
            prefix_after.st_mode,
            prefix_after.st_nlink,
        ) != prefix_identity or not prefix_empty_after:
            raise ChildProcessError("selected child pycache prefix is not empty after exit")
        if stdout or stderr:
            raise ChildProcessError("successful child emitted diagnostic bytes")
        observation = {
            "argv": list(argv),
            "argv_sha256": envelope["ordered_argv_sha256"],
            "child_input_schema_version": CHILD_INPUT_SCHEMA_VERSION,
            "child_role": role,
            "cross_field_binding": True,
            "diagnostics_empty": True,
            "entrypoint_source": result.entrypoint_source.model_dump(mode="json"),
            "exit_code": process.returncode,
            "final_uv_value": environment["UV"],
            "frame_count": 1,
            "frame_eof": True,
            "frame_magic": FRAME_MAGIC.decode("ascii"),
            "frame_payload_sha256": _sha256(payload),
            "frame_payload_size_bytes": len(payload),
            "frame_version": FRAME_VERSION,
            "in_place_pyc_unchanged": True,
            "initial_uv_value": environment["UV"],
            "nonce": nonce,
            "not_timed_out": True,
            "payload_kind": result.payload_kind,
            "prefix_absolute_path": os.fspath(pycache_prefix),
            "prefix_empty_after": prefix_empty_after,
            "prefix_empty_before": prefix_empty_before,
            "prefix_identity_after": prefix_identity_after,
            "prefix_identity_before": prefix_identity_before,
            "prefix_identity_unchanged": prefix_identity_after == prefix_identity_before,
            "prefix_relative_path": envelope["pycache_prefix_relative"],
            "process_id": process.pid,
            "result_descriptor_inheritable": result_descriptor_inheritable,
            "result_descriptor_number": envelope["result_descriptor_number"],
            "result_descriptor_parent_closed": result_descriptor_parent_closed,
            "result_schema_version": result.schema_version,
            "source_descriptor_checkpoint": True,
            "stderr_sha256": _sha256(stderr),
            "stderr_size_bytes": len(stderr),
            "stdout_sha256": _sha256(stdout),
            "stdout_size_bytes": len(stdout),
            "timeout_milliseconds": int(timeout * 1000),
            "transport_environment_sha256": expected_transport_environment_sha256,
            "uv_path_resolution": uv_path_resolution,
            "zero_in_place_pyc_reads": True,
        }
        expected_facts = {
            "entrypoint_source": result.entrypoint_source.model_dump(mode="json"),
            "frame_payload_sha256": _sha256(payload),
            "frame_payload_size_bytes": len(payload),
            "nonce": nonce,
            "prefix_absolute_path": os.fspath(pycache_prefix),
            "prefix_identity_after": prefix_identity_after,
            "prefix_identity_before": prefix_identity_before,
            "prefix_relative_path": envelope["pycache_prefix_relative"],
            "process_id": process.pid,
            "result_descriptor_number": envelope["result_descriptor_number"],
            "timeout_milliseconds": int(timeout * 1000),
            "transport_environment_sha256": expected_transport_environment_sha256,
        }
        _validate_child_process_observation(
            observation, expected_role=role, expected_facts=expected_facts
        )
        observation_bytes = _canonical_json_bytes(observation)
        process_evidence = ChildProcessEvidence(
            expected_facts_bytes=_canonical_json_bytes(expected_facts),
            observation_bytes=observation_bytes,
            payload_bytes=payload,
            role=role,
        )
        process_evidence.validate(result)
        return ChildExecution(
            envelope=result,
            stdout=stdout,
            stderr=stderr,
            process_evidence=process_evidence,
        )
    finally:
        if result_writer >= 0:
            os.close(result_writer)
        os.close(result_reader)
        os.close(source.descriptor)


def _admission_inputs(
    admission_run_id: str,
    prefix_relative_path: str,
    repository_code_sha256: str,
    *,
    project_root: Path | None = None,
    launcher_sha256: str | None = None,
    launcher_size: int | None = None,
) -> dict[str, object]:
    project_root = (project_root or Path.cwd()).absolute()
    if launcher_sha256 is None or launcher_size is None:
        launcher_raw = _guard_read_relative(project_root, "scripts/launch_wyscout_v5.py")
        launcher_sha256 = _sha256(launcher_raw)
        launcher_size = len(launcher_raw)
    bootstrap_authority = _outer_bootstrap_tuple(
        project_root=project_root,
        launcher_sha256=launcher_sha256,
        launcher_size=launcher_size,
    )
    return {
        "admission_prefix_relative_path": prefix_relative_path,
        "admission_run_id": admission_run_id,
        "bootstrap_tuple_sha256": _sha256(_canonical_json_bytes(bootstrap_authority)),
        "code_manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "pyproject_sha256": PYPROJECT_SHA256,
        "repository_code_sha256": repository_code_sha256,
        "selected_dependency_groups": [
            "data",
            "e2e",
            "lint-type",
            "model",
            "orchestration",
            "runtime",
            "security",
            "test",
        ],
        "uv_lock_sha256": UV_LOCK_SHA256,
    }


def _validate_manifest_bytes(
    contracts: ModuleType,
    admission: "PreBuildAdmissionResult",
    expected_components: dict[str, object],
    counts: tuple[int, ...],
) -> bytes:
    contracts.validate_admission_component_authority(
        admission,
        expected_components,
        tuple(zip(COMPONENT_KEYS, counts, strict=True)),
    )
    padded = admission.canonical_manifest_bytes_b64u + "=" * (
        -len(admission.canonical_manifest_bytes_b64u) % 4
    )
    raw = base64.urlsafe_b64decode(padded.encode("ascii"))
    if _sha256(raw) != admission.canonical_manifest_sha256:
        raise RuntimeControlError("admission manifest digest changed after validation")
    return raw


def _read_published_manifest(path: Path, expected: bytes) -> bytes:
    before = os.stat(path, follow_symlinks=False)
    if (
        not stat.S_ISREG(before.st_mode)
        or stat.S_ISLNK(before.st_mode)
        or stat.S_IMODE(before.st_mode) != 0o600
        or before.st_nlink != 1
        or before.st_size != len(expected)
    ):
        raise RuntimeControlError("published code manifest metadata differs")
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        opened = os.fstat(descriptor)
        if (before.st_dev, before.st_ino, before.st_size) != (
            opened.st_dev,
            opened.st_ino,
            opened.st_size,
        ):
            raise RuntimeControlError("published code manifest changed while opening")
        raw = b""
        while chunk := os.read(descriptor, 1024 * 1024):
            raw += chunk
        after = os.fstat(descriptor)
        if (opened.st_dev, opened.st_ino, opened.st_size) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
        ) or raw != expected:
            raise RuntimeControlError("published code manifest readback differs")
        return raw
    finally:
        os.close(descriptor)


def _guard_read_content_addressed_manifest(path: Path, expected_sha256: str) -> bytes:
    if SHA256_RE.fullmatch(expected_sha256) is None:
        raise RuntimeControlError("content-addressed manifest digest is malformed")
    before = os.stat(path, follow_symlinks=False)
    if (
        not stat.S_ISREG(before.st_mode)
        or stat.S_ISLNK(before.st_mode)
        or stat.S_IMODE(before.st_mode) != 0o600
        or before.st_nlink != 1
        or not 1 <= before.st_size <= 12_000_000
    ):
        raise RuntimeControlError("content-addressed manifest metadata differs")
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        opened = os.fstat(descriptor)
        if (before.st_dev, before.st_ino, before.st_size) != (
            opened.st_dev,
            opened.st_ino,
            opened.st_size,
        ):
            raise RuntimeControlError("content-addressed manifest changed while opening")
        chunks: list[bytes] = []
        while chunk := os.read(descriptor, 1024 * 1024):
            chunks.append(chunk)
        after = os.fstat(descriptor)
        raw = b"".join(chunks)
        if (
            (opened.st_dev, opened.st_ino, opened.st_size)
            != (after.st_dev, after.st_ino, after.st_size)
            or len(raw) != after.st_size
            or _sha256(raw) != expected_sha256
        ):
            raise RuntimeControlError("content-addressed manifest readback differs")
        _load_canonical_json(raw)
        return raw
    finally:
        os.close(descriptor)


def prepare_wyscout_v5_launch(
    *,
    project_root: Path,
    roots: RuntimeControlRoots,
    run_id: str,
    admission_run_id: str | None = None,
    timeout: float = CHILD_TIMEOUT_SECONDS,
    retained_launcher_sha256: str | None = None,
    retained_launcher_size: int | None = None,
) -> WyscoutLaunchPlan:
    """Admit, publish/read back code authority, and return the frozen launch plan."""

    project_root = project_root.absolute()
    if retained_launcher_sha256 is None or retained_launcher_size is None:
        launcher_raw = _guard_read_relative(project_root, "scripts/launch_wyscout_v5.py")
        retained_launcher_sha256 = _sha256(launcher_raw)
        retained_launcher_size = len(launcher_raw)
    if (
        SHA256_RE.fullmatch(retained_launcher_sha256) is None
        or type(retained_launcher_size) is not int
        or retained_launcher_size <= 0
    ):
        raise RuntimeControlError("retained launcher byte authority is malformed")
    run_id = _safe_uuid4(run_id, label="run_id")
    admission_run_id = _safe_uuid4(admission_run_id or str(uuid4()), label="admission_run_id")
    if admission_run_id == run_id:
        raise RuntimeControlError("admission and rebuild operational UUIDs must differ")
    _guard_v2_aggregates(project_root)
    pyproject = _guard_read_relative(project_root, "pyproject.toml")
    lock = _guard_read_relative(project_root, "uv.lock", max_bytes=128 * 1024 * 1024)
    if _sha256(pyproject) != PYPROJECT_SHA256 or _sha256(lock) != UV_LOCK_SHA256:
        raise RuntimeControlError("accepted pyproject/uv.lock bytes drifted")
    repository_digest, components, counts = _admission_authority(project_root)
    prefix_relative = (
        "data/working/wyscout/v5/.staging/admission/"
        f"admission_run_id={admission_run_id}/runtime-pycache"
    )
    prefix = _create_empty_prefix(
        roots.pycache_staging_root, "PRE_BUILD_ADMISSION", admission_run_id, None
    )
    child = _run_child(
        project_root=project_root,
        argv=ADMISSION_ARGV,
        role="PRE_BUILD_ADMISSION",
        inputs=_admission_inputs(
            admission_run_id,
            prefix_relative,
            repository_digest,
            project_root=project_root,
            launcher_sha256=retained_launcher_sha256,
            launcher_size=retained_launcher_size,
        ),
        expected_repository_code_sha256=repository_digest,
        pycache_prefix=prefix,
        timeout=timeout,
        retained_launcher_sha256=retained_launcher_sha256,
    )
    contracts, publication = _runtime_contracts(project_root)
    admission = cast("PreBuildAdmissionResult", child.envelope.result)
    if not isinstance(admission, contracts.PreBuildAdmissionResult):
        raise RuntimeControlError("admission child returned the wrong payload arm")
    manifest_bytes = _validate_manifest_bytes(contracts, admission, components, counts)
    _ensure_mode_0700_directory(roots.manifest_staging_root)
    manifest_tail = f"code/{admission.canonical_manifest_sha256}.code-manifest.json"
    manifest_relative = f"data/manifests/wyscout/v5/{manifest_tail}"
    publisher = publication.WyscoutStagedPublisher(
        {
            "wyscout-manifests": publication.WyscoutPublicationRoot(
                final_root=roots.manifest_final_root,
                staging_root=roots.manifest_staging_root,
            )
        }
    )

    def validator(candidate: bytes) -> None:
        if candidate != manifest_bytes or _load_canonical_json(candidate) != json.loads(candidate):
            raise RuntimeControlError("staged code manifest differs from canonical admission")

    def final_recheck() -> None:
        _guard_v2_aggregates(project_root)
        after_repository, after_components, after_counts = _admission_authority(project_root)
        if (after_repository, after_components, after_counts) != (
            repository_digest,
            components,
            counts,
        ):
            raise RuntimeControlError("stable component authority drifted before publication")

    published = publisher.publish_bytes(
        "wyscout-manifests",
        manifest_tail,
        manifest_bytes,
        validator=validator,
        final_recheck=final_recheck,
    )
    if (
        published.physical_sha256 != admission.canonical_manifest_sha256
        or published.size_bytes != len(manifest_bytes)
    ):
        raise RuntimeControlError("publisher result differs from admitted manifest")
    readback = _read_published_manifest(roots.manifest_final_root / manifest_tail, manifest_bytes)
    if _sha256(readback) != admission.canonical_manifest_sha256:
        raise RuntimeControlError("immutable code-manifest readback digest differs")
    projection = contracts.PreBuildProjection(
        authority_rows=contracts.accepted_authority_rows(),
        code_manifest_id=contracts.code_manifest_id_for_digest(admission.canonical_manifest_sha256),
        code_manifest_sha256=admission.canonical_manifest_sha256,
        dependency_rows=contracts.accepted_dependency_rows(),
        environment_digest=admission.environment_digest,
        local_resource_digest=cast(str, components["local_resource_digest"]),
        product_contract_digest=PRODUCT_CONTRACT_V2_LOGICAL_SHA256,
        schema_bundle_digest=SCHEMA_BUNDLE_V2_LOGICAL_SHA256,
        selected_lock_closure_digest=cast(str, components["selected_lock_closure_digest"]),
    )
    build_id = contracts.build_id_for_projection(projection)
    invocation = contracts.invocation_from_projection(projection)
    if (
        invocation.build_id != build_id
        or contracts.projection_from_invocation(invocation) != projection
    ):
        raise RuntimeControlError("projection/invocation strict inverse differs")
    layers = cast(
        tuple[str, str, str],
        tuple(
            contracts.layer_manifest_path(layer, build_id) for layer in ("BRONZE", "SILVER", "GOLD")
        ),
    )
    return WyscoutLaunchPlan(
        build_id=build_id,
        run_id=run_id,
        code_manifest_id=projection.code_manifest_id,
        code_manifest_sha256=projection.code_manifest_sha256,
        code_manifest_relative_path=manifest_relative,
        layer_manifest_relative_paths=layers,
        rebuild_prefix_relative_path=(
            f"data/working/wyscout/v5/.staging/{build_id}/{run_id}/runtime-pycache"
        ),
        rebuild_receipt_relative_path=contracts.rebuild_receipt_path(build_id, run_id),
        rebuild_argv=REBUILD_ARGV,
        invocation=invocation,
        admission_process_evidence=child.process_evidence,
    )


def execute_rebuild_child(
    *,
    project_root: Path,
    roots: RuntimeControlRoots,
    plan: WyscoutLaunchPlan,
    timeout: float = CHILD_TIMEOUT_SECONDS,
    retained_launcher_sha256: str | None = None,
) -> ChildExecution:
    """Execute and validate the frozen rebuild argv; never called during preparation."""

    project_root = project_root.absolute()
    contracts, _publication = _runtime_contracts(project_root)
    _guard_v2_aggregates(project_root)
    pyproject = _guard_read_relative(project_root, "pyproject.toml")
    lock = _guard_read_relative(project_root, "uv.lock", max_bytes=128 * 1024 * 1024)
    if _sha256(pyproject) != PYPROJECT_SHA256 or _sha256(lock) != UV_LOCK_SHA256:
        raise RuntimeControlError("rebuild lock-input bytes differ from admission")
    before_repository, before_components, before_counts = _admission_authority(project_root)
    if tuple(plan.rebuild_argv) != REBUILD_ARGV:
        raise RuntimeControlError("rebuild argv differs from the frozen authority")
    if (
        contracts.invocation_from_projection(contracts.projection_from_invocation(plan.invocation))
        != plan.invocation
    ):
        raise RuntimeControlError("rebuild invocation no longer has a strict inverse")
    if (
        plan.invocation.build_id != plan.build_id
        or plan.run_id not in plan.rebuild_prefix_relative_path
    ):
        raise RuntimeControlError("rebuild plan build/run binding differs")
    prefix = _create_empty_prefix(
        roots.pycache_staging_root,
        "POST_BUILD_ID_REBUILD",
        plan.run_id,
        plan.build_id,
    )
    inputs: dict[str, object] = {
        "build_id": plan.build_id,
        "code_manifest_id": plan.code_manifest_id,
        "code_manifest_relative_path": plan.code_manifest_relative_path,
        "code_manifest_sha256": plan.code_manifest_sha256,
        "environment_digest": plan.invocation.environment_digest,
        "layer_manifest_relative_paths": list(plan.layer_manifest_relative_paths),
        "rebuild_invocation": plan.invocation.model_dump(mode="json"),
        "rebuild_prefix_relative_path": plan.rebuild_prefix_relative_path,
        "rebuild_receipt_relative_path": plan.rebuild_receipt_relative_path,
        "run_id": plan.run_id,
    }
    manifest_path = (
        roots.manifest_final_root / "code" / f"{plan.code_manifest_sha256}.code-manifest.json"
    )
    manifest_bytes = _guard_read_content_addressed_manifest(
        manifest_path, plan.code_manifest_sha256
    )
    manifest_object = _load_canonical_json(manifest_bytes)
    if type(manifest_object) is not dict:
        raise RuntimeControlError("content-addressed code manifest is not an object")
    expected_manifest = {
        **before_components,
        "environment_digest": _sha256_json(before_components),
        "repository_code_sha256": before_repository,
        "schema_version": MANIFEST_SCHEMA_VERSION,
    }
    if manifest_object != expected_manifest:
        raise RuntimeControlError("content-addressed manifest differs from fresh stable authority")
    repository_code_sha256 = before_repository
    projection = contracts.projection_from_invocation(plan.invocation)
    if (
        plan.code_manifest_id != projection.code_manifest_id
        or plan.code_manifest_sha256 != projection.code_manifest_sha256
        or plan.invocation.environment_digest != expected_manifest["environment_digest"]
        or plan.invocation.local_resource_digest != before_components["local_resource_digest"]
        or plan.invocation.selected_lock_closure_digest
        != before_components["selected_lock_closure_digest"]
        or plan.invocation.schema_bundle_digest != SCHEMA_BUNDLE_V2_LOGICAL_SHA256
        or plan.invocation.product_contract_digest != PRODUCT_CONTRACT_V2_LOGICAL_SHA256
    ):
        raise RuntimeControlError("rebuild plan differs from freshly reconstructed authority")
    runtime_subset_authority = _freeze_independent_runtime_subset_authority(project_root)
    child = _run_child(
        project_root=project_root,
        argv=REBUILD_ARGV,
        role="POST_BUILD_ID_REBUILD",
        inputs=inputs,
        expected_repository_code_sha256=repository_code_sha256,
        pycache_prefix=prefix,
        timeout=timeout,
        retained_launcher_sha256=retained_launcher_sha256,
    )
    if child.envelope.child_role != "POST_BUILD_ID_REBUILD":
        raise RuntimeControlError("generic rebuild execution returned the wrong child role")
    if child.process_evidence.role != "POST_BUILD_ID_REBUILD":
        raise RuntimeControlError("rebuild process evidence role differs")
    child.process_evidence.validate(child.envelope)
    result = child.envelope.result
    if not isinstance(result, contracts.PostBuildIdRebuildResult):
        raise RuntimeControlError("rebuild child returned the wrong payload arm")
    runtime_subset_authority.validate(result.final_recheck)
    if (
        result.build_id != plan.build_id
        or result.run_id != plan.run_id
        or result.rebuild_prefix_relative_path != plan.rebuild_prefix_relative_path
        or result.rebuild_receipt.relative_path != plan.rebuild_receipt_relative_path
        or tuple(row.manifest_relative_path for row in result.layer_manifests)
        != plan.layer_manifest_relative_paths
        or result.final_recheck.environment_digest != plan.invocation.environment_digest
        or result.final_recheck.resource_digest != plan.invocation.local_resource_digest
        or result.final_recheck.repository_code_sha256 != before_repository
    ):
        raise RuntimeControlError("rebuild result/final recheck differs from frozen plan")
    _guard_v2_aggregates(project_root)
    after_authority = _admission_authority(project_root)
    if after_authority != (before_repository, before_components, before_counts):
        raise RuntimeControlError("stable authority drifted across rebuild execution")
    if (
        _guard_read_content_addressed_manifest(manifest_path, plan.code_manifest_sha256)
        != manifest_bytes
    ):
        raise RuntimeControlError("content-addressed manifest drifted across rebuild execution")
    if tuple(os.scandir(prefix)):
        raise RuntimeControlError("rebuild prefix is nonempty after final retained recheck")
    return child


def _require_empty_prefix(path: Path, *, expected_identity: tuple[int, ...] | None = None) -> None:
    metadata = os.stat(path, follow_symlinks=False)
    identity = (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_mode,
        metadata.st_nlink,
    )
    if (
        not stat.S_ISDIR(metadata.st_mode)
        or stat.S_ISLNK(metadata.st_mode)
        or stat.S_IMODE(metadata.st_mode) != 0o700
        or (expected_identity is not None and identity != expected_identity)
        or tuple(os.scandir(path))
    ):
        raise RuntimeControlError("retained runtime prefix is replaced, unsafe, or nonempty")


def _mode_0700_directory_identity(path: Path) -> tuple[int, int, int, int]:
    metadata = os.stat(path, follow_symlinks=False)
    if (
        not stat.S_ISDIR(metadata.st_mode)
        or stat.S_ISLNK(metadata.st_mode)
        or stat.S_IMODE(metadata.st_mode) != 0o700
    ):
        raise RuntimeControlError("retained runtime directory is unsafe")
    return (metadata.st_dev, metadata.st_ino, metadata.st_mode, metadata.st_nlink)


def _require_directory_identity(path: Path, expected: tuple[int, int, int, int]) -> None:
    if _mode_0700_directory_identity(path) != expected:
        raise RuntimeControlError("retained runtime directory identity drifted")


def _recheck_outer_bootstrap(bootstrap: dict[str, object]) -> None:
    descriptor = cast(int, bootstrap["launcher_source_fd"])
    expected_identity = cast(tuple[int, int, int, int, int], bootstrap["launcher_identity"])
    metadata = os.fstat(descriptor)
    current_identity = (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_mode,
        metadata.st_nlink,
        metadata.st_size,
    )
    if (
        current_identity != expected_identity
        or os.get_inheritable(descriptor)
        or os.lseek(descriptor, 0, os.SEEK_CUR) != 0
    ):
        raise RuntimeControlError("retained outer launcher descriptor drifted")
    chunks: list[bytes] = []
    offset = 0
    while offset < metadata.st_size:
        chunk = os.pread(descriptor, min(1024 * 1024, metadata.st_size - offset), offset)
        if not chunk:
            raise RuntimeControlError("retained outer launcher descriptor ended early")
        chunks.append(chunk)
        offset += len(chunk)
    if (
        os.pread(descriptor, 1, metadata.st_size) != b""
        or os.lseek(descriptor, 0, os.SEEK_CUR) != 0
        or _sha256(b"".join(chunks)) != bootstrap["launcher_sha256"]
    ):
        raise RuntimeControlError("retained outer launcher bytes drifted")
    _require_empty_prefix(
        Path(cast(str, bootstrap["control_prefix"])),
        expected_identity=cast(tuple[int, ...], bootstrap["control_identity"]),
    )


def _outer_runtime_roots(project_root: Path, admission_run_id: str) -> RuntimeControlRoots:
    staging = project_root / "data/working/wyscout/v5/.staging"
    return RuntimeControlRoots(
        manifest_final_root=project_root / "data/manifests/wyscout/v5",
        manifest_staging_root=(
            staging / "admission" / f"admission_run_id={admission_run_id}" / "manifest-staging"
        ),
        pycache_staging_root=staging,
    )


def _pyc_inventory_health(
    snapshot: tuple[dict[str, object], ...],
) -> dict[str, object]:
    authority_counts: dict[str, int] = {}
    entry_kind_counts: dict[str, int] = {}
    role_counts: dict[str, int] = {}
    for row in snapshot:
        for key, target in (
            ("authority_class", authority_counts),
            ("entry_kind", entry_kind_counts),
            ("role", role_counts),
        ):
            value = row.get(key)
            if type(value) is str:
                target[value] = target.get(value, 0) + 1
    return {
        "authority_class_counts": {key: authority_counts[key] for key in sorted(authority_counts)},
        "entry_kind_counts": {key: entry_kind_counts[key] for key in sorted(entry_kind_counts)},
        "inventory_authority": "AUDIT_ONLY_ZERO_READ_USE",
        "inventory_sha256": _sha256(_canonical_json_bytes(snapshot)),
        "portable_security_projection_sha256": _sha256_json(
            _independent_pyc_security_projection(snapshot)
        ),
        "role_counts": {key: role_counts[key] for key in sorted(role_counts)},
        "row_count": len(snapshot),
    }


def _require_matching_runtime_subset_evidence(
    first: dict[str, object], second: dict[str, object]
) -> None:
    """Reject a two-root health comparison with different exact terminal R evidence."""

    normalized: list[bytes] = []
    for value in (first, second):
        if tuple(value) != ("runtime_subset_digest", "runtime_subset_rows"):
            raise RuntimeControlError("two-root runtime evidence roster/order differs")
        digest = value["runtime_subset_digest"]
        rows = value["runtime_subset_rows"]
        if type(digest) is not str or type(rows) is not list:
            raise RuntimeControlError("two-root runtime evidence shape differs")
        if digest != _sha256_json({"algorithm": RUNTIME_SUBSET_ALGORITHM, "rows": rows}):
            raise RuntimeControlError("two-root runtime evidence digest differs from rows")
        normalized.append(_canonical_json_bytes(value))
    if normalized[0] != normalized[1]:
        raise RuntimeControlError("two-root runtime subsets differ")


def _require_outer_authority_snapshot(
    project_root: Path,
    expected: tuple[
        str,
        dict[str, object],
        tuple[int, ...],
        tuple[dict[str, object], ...],
    ],
) -> None:
    current = _admission_authority_with_pyc(project_root)
    if current[:3] != expected[:3] or _independent_pyc_security_projection(
        current[3]
    ) != _independent_pyc_security_projection(expected[3]):
        raise RuntimeControlError("whole-launch stable/portable PYC security authority drifted")


def _validate_outer_completion_status(status: dict[str, object]) -> bytes:
    if tuple(status) != (
        "admission_run_id",
        "build_id",
        "child_process_observations",
        "code_manifest_sha256",
        "control_run_id",
        "outer_transport_environment_sha256",
        "pyc_inventory_health",
        "rebuild_receipt_relative_path",
        "rebuild_receipt_sha256",
        "run_id",
        "runtime_subset_digest",
        "runtime_subset_rows",
        "schema_version",
        "status",
    ):
        raise RuntimeControlError("outer completion top-level roster/order differs")
    if (
        status["schema_version"] != "w04-local-control-completion-v2"
        or status["status"] != "COMPLETE"
    ):
        raise RuntimeControlError("outer completion version/status differs")
    process_rows = status["child_process_observations"]
    if (
        type(process_rows) is not list
        or len(process_rows) != 2
        or any(type(row) is not dict for row in process_rows)
    ):
        raise RuntimeControlError("outer completion process row cardinality/shape differs")
    _validate_child_process_observation(
        cast(dict[str, object], process_rows[0]), expected_role="PRE_BUILD_ADMISSION"
    )
    _validate_child_process_observation(
        cast(dict[str, object], process_rows[1]), expected_role="POST_BUILD_ID_REBUILD"
    )
    runtime_subset_digest = status["runtime_subset_digest"]
    runtime_subset_rows = status["runtime_subset_rows"]
    if (
        type(runtime_subset_digest) is not str
        or type(runtime_subset_rows) is not list
        or runtime_subset_digest
        != _sha256_json({"algorithm": RUNTIME_SUBSET_ALGORITHM, "rows": runtime_subset_rows})
    ):
        raise RuntimeControlError("outer completion runtime evidence differs")
    status_bytes = _canonical_json_bytes(status)
    if _load_canonical_json(status_bytes) != status:
        raise RuntimeControlError("outer completion status is not canonical")
    return status_bytes


def _execute_outer_control(bootstrap: dict[str, object]) -> bytes:
    project_root = Path(cast(str, bootstrap["project_root"])).absolute()
    if project_root != Path.cwd().absolute():
        raise RuntimeControlError("outer execution cwd differs from bootstrap")
    control_run_id = _safe_uuid4(cast(str, bootstrap["control_run_id"]), label="control_run_id")
    retained_authority = _admission_authority_with_pyc(project_root)
    retained_pyc = retained_authority[3]
    admission_run_id = _sample_distinct_uuid4(excluded={control_run_id}, label="admission_run_id")
    run_id = _sample_distinct_uuid4(excluded={control_run_id, admission_run_id}, label="run_id")
    roots = _outer_runtime_roots(project_root, admission_run_id)
    _recheck_outer_bootstrap(bootstrap)
    plan = prepare_wyscout_v5_launch(
        project_root=project_root,
        roots=roots,
        run_id=run_id,
        admission_run_id=admission_run_id,
        retained_launcher_sha256=cast(str, bootstrap["launcher_sha256"]),
        retained_launcher_size=cast(
            int, cast(dict[str, object], bootstrap["bootstrap_tuple"])["launcher_size"]
        ),
    )
    admission_prefix = (
        roots.pycache_staging_root
        / "admission"
        / f"admission_run_id={admission_run_id}"
        / "runtime-pycache"
    )
    admission_identity = _mode_0700_directory_identity(admission_prefix)
    manifest_staging_identity = _mode_0700_directory_identity(roots.manifest_staging_root)
    _recheck_outer_bootstrap(bootstrap)
    _require_outer_authority_snapshot(project_root, retained_authority)
    execution = execute_rebuild_child(
        project_root=project_root,
        roots=roots,
        plan=plan,
        retained_launcher_sha256=cast(str, bootstrap["launcher_sha256"]),
    )
    rebuild_prefix = roots.pycache_staging_root / plan.build_id / run_id / "runtime-pycache"
    rebuild_identity = _mode_0700_directory_identity(rebuild_prefix)
    _recheck_outer_bootstrap(bootstrap)
    _require_outer_authority_snapshot(project_root, retained_authority)
    _require_empty_prefix(admission_prefix, expected_identity=admission_identity)
    _require_empty_prefix(rebuild_prefix, expected_identity=rebuild_identity)
    _require_directory_identity(roots.manifest_staging_root, manifest_staging_identity)
    if tuple(roots.manifest_staging_root.rglob("*.partial")):
        raise RuntimeControlError("admission manifest staging retained a partial file")
    result = execution.envelope.result
    rebuild_receipt = getattr(result, "rebuild_receipt", None)
    receipt_digest = getattr(rebuild_receipt, "sha256", None)
    if type(receipt_digest) is not str or SHA256_RE.fullmatch(receipt_digest) is None:
        raise RuntimeControlError("rebuild completion lacks its exact receipt digest")
    final_recheck = getattr(result, "final_recheck", None)
    runtime_subset_digest = getattr(final_recheck, "runtime_subset_digest", None)
    runtime_subset_models = getattr(final_recheck, "runtime_subset_rows", None)
    if type(runtime_subset_digest) is not str or type(runtime_subset_models) is not tuple:
        raise RuntimeControlError("rebuild completion lacks normalized runtime evidence")
    runtime_subset_rows = [row.model_dump(mode="json") for row in runtime_subset_models]
    if runtime_subset_digest != _sha256_json(
        {"algorithm": RUNTIME_SUBSET_ALGORITHM, "rows": runtime_subset_rows}
    ):
        raise RuntimeControlError("outer runtime evidence copy differs before completion")
    if (
        plan.admission_process_evidence.role != "PRE_BUILD_ADMISSION"
        or execution.process_evidence.role != "POST_BUILD_ID_REBUILD"
    ):
        raise RuntimeControlError("outer child process evidence order/role differs")
    admission_process_observation = plan.admission_process_evidence.validate()
    rebuild_process_observation = execution.process_evidence.validate(execution.envelope)
    status = {
        "admission_run_id": admission_run_id,
        "build_id": plan.build_id,
        "child_process_observations": [
            admission_process_observation,
            rebuild_process_observation,
        ],
        "code_manifest_sha256": plan.code_manifest_sha256,
        "control_run_id": control_run_id,
        "outer_transport_environment_sha256": bootstrap["environment_sha256"],
        "pyc_inventory_health": _pyc_inventory_health(retained_pyc),
        "rebuild_receipt_relative_path": plan.rebuild_receipt_relative_path,
        "rebuild_receipt_sha256": receipt_digest,
        "run_id": run_id,
        "runtime_subset_digest": runtime_subset_digest,
        "runtime_subset_rows": runtime_subset_rows,
        "schema_version": "w04-local-control-completion-v2",
        "status": "COMPLETE",
    }
    status_bytes = _validate_outer_completion_status(status)
    _recheck_outer_bootstrap(bootstrap)
    _require_outer_authority_snapshot(project_root, retained_authority)
    _require_empty_prefix(admission_prefix, expected_identity=admission_identity)
    _require_empty_prefix(rebuild_prefix, expected_identity=rebuild_identity)
    _require_directory_identity(roots.manifest_staging_root, manifest_staging_identity)
    return status_bytes


def main() -> int:
    if type(_W04_EARLY_BOOTSTRAP) is not dict:
        raise RuntimeControlError("direct execution lacks the verified outer bootstrap")
    bootstrap = _W04_EARLY_BOOTSTRAP
    descriptor = cast(int, bootstrap["launcher_source_fd"])
    try:
        status = _execute_outer_control(bootstrap)
        sys.stdout.buffer.write(status + b"\n")
        sys.stdout.buffer.flush()
        return 0
    finally:
        try:
            _recheck_outer_bootstrap(bootstrap)
        finally:
            os.close(descriptor)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"W04 runtime control rejected: {error}", file=sys.stderr)
        raise SystemExit(2) from error

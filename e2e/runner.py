import os
import nose
import nose_launchable
import subprocess


def run_subset_target():
    args = [
        "tests/dir1/test1.py",
        "tests/dir1/test2.py",
        "tests/dir2/test1.py",
        "tests/dir2/test2.py",
        "tests/dir3/test1.py",
        "--launchable-subset",
        "--launchable-build-number",
        os.getenv("GITHUB_RUN_ID"),
        "--launchable-subset-target",
        "10",
        "-sv"
    ]

    plugins = [nose_launchable.plugin.Plugin()]
    return nose.core.run(argv=args, addplugins=plugins)


def run_subset_options():
    args = [
        "tests/dir1/test1.py",
        "tests/dir1/test2.py",
        "tests/dir2/test1.py",
        "tests/dir2/test2.py",
        "tests/dir3/test1.py",
        "--launchable-subset",
        "--launchable-build-number",
        os.getenv("GITHUB_RUN_ID"),
        "--launchable-subset-options",
        "--target 10%",
        "-sv"
    ]

    plugins = [nose_launchable.plugin.Plugin()]
    return nose.core.run(argv=args, addplugins=plugins)


def run_split_subset():
    args = [
        "tests/dir1/test1.py",
        "tests/dir1/test2.py",
        "tests/dir2/test1.py",
        "tests/dir2/test2.py",
        "tests/dir3/test1.py",
        "--launchable-subset",
        "--launchable-build-number",
        os.getenv("GITHUB_RUN_ID"),
        "--launchable-subset-options",
        "--target 80% --bin 1/2",
        "-sv"
    ]

    plugins = [nose_launchable.plugin.Plugin()]
    return nose.core.run(argv=args, addplugins=plugins)


def run_split_subset_with_test_session():
    build_number = "{}-split-subset".format(os.getenv("GITHUB_RUN_ID"))
    record_build_cmd = ["launchable", "record", "build",
                        "--name", build_number, "--no-commit-collection"]
    subprocess.run(record_build_cmd)

    record_session_cmd = ["launchable", "record",
                          "session", "--build", build_number]
    result = subprocess.run(
        record_session_cmd, stdout=subprocess.PIPE, encoding='utf-8',)
    session = result.stdout.rstrip("\n")

    args = [
        "tests/dir1/test1.py",
        "tests/dir1/test2.py",
        "tests/dir2/test1.py",
        "tests/dir2/test2.py",
        "tests/dir3/test1.py",
        "--launchable-subset",
        "--launchable-test-session",
        session,
        "--launchable-subset-options",
        "--target 80% --bin 1/2",
        "-sv"
    ]

    plugins = [nose_launchable.plugin.Plugin()]
    return nose.core.run(argv=args, addplugins=plugins)


def run_record_only():
    args = [
        "tests/dir1/test1.py",
        "tests/dir1/test2.py",
        "tests/dir2/test1.py",
        "tests/dir2/test2.py",
        "tests/dir3/test1.py",
        "--launchable-record-only",
        "--launchable-build-number",
        os.getenv("GITHUB_RUN_ID"),
        "-sv"
    ]

    plugins = [nose_launchable.plugin.Plugin()]
    return nose.core.run(argv=args, addplugins=plugins)


if __name__ == '__main__':
    run_subset_target()
    run_subset_options()
    run_split_subset()
    run_split_subset_with_test_session()
    run_record_only()

import pytest
from mockito import when, unstub, verify
from asr import ASR


def test_run_asr(application_settings):
    try:
        asr = ASR(application_settings)

    finally:
        unstub()


def test_process_asr_output(application_settings):
    try:
        asr = ASR(application_settings)

    finally:
        unstub()


def test_validate_asr_output(application_settings):
    try:
        asr = ASR(application_settings)

    finally:
        unstub()


def test_package_output(application_settings):
    try:
        asr = ASR(application_settings)

    finally:
        unstub()


def test_create_word_json(application_settings):
    try:
        asr = ASR(application_settings)

    finally:
        unstub()


def test_get_output_dir(application_settings):
    try:
        asr = ASR(application_settings)

    finally:
        unstub()


def test_get_transcript_file_path(application_settings):
    try:
        asr = ASR(application_settings)

    finally:
        unstub()

def test_get_words_file_path(application_settings):
    try:
        asr = ASR(application_settings)

    finally:
        unstub()
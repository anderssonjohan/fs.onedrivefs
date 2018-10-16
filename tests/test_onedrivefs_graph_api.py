# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from datetime import datetime
from json import dump, load
from os import environ
from time import sleep
from unittest import TestCase
from uuid import uuid4

from fs.test import FSTestCases
from fs.onedrivefs.onedrivefs_graph_api import OneDriveFSGraphAPI

class InMemoryTokenSaver: # pylint: disable=too-few-public-methods
	def __init__(self, path):
		self.path = path

	def __call__(self, token):
		with open(self.path, "w") as f:
			dump(token, f)

class TokenStorageFile:
	def __init__(self, path):
		self.path = path

	def Save(self, token):
		with open(self.path, "w") as f:
			dump(token, f)

	def Load(self):
		try:
			with open(self.path, "r") as f:
				return load(f)
		except FileNotFoundError:
			return None

class TestOneDriveFS(FSTestCases, TestCase):
	def make_fs(self):
		storage = TokenStorageFile(environ["GRAPH_API_TOKEN_PATH"])
		self.fullFS = OneDriveFSGraphAPI(environ["GRAPH_API_CLIENT_ID"], environ["GRAPH_API_CLIENT_SECRET"], storage.Load(), storage.Save) # pylint: disable=attribute-defined-outside-init
		self.testSubdir = "/Documents/test-onedrivefs/" + str(uuid4()) # pylint: disable=attribute-defined-outside-init
		return self.fullFS.makedirs(self.testSubdir)

	def destroy_fs(self, _):
		pass #self.fullFS.removetree(self.testSubdir)

	def test_overwrite_file(self):
		with self.fs.open("small_file_to_overwrite.bin", "wb") as f:
			f.write(b"x" * 10)

		with self.fs.open("small_file_to_overwrite.bin", "wb") as f:
			f.write(b"y" * 10)

		with self.fs.open("small_file_to_overwrite.txt", "w") as f:
			f.write("x" * 10)

		with self.fs.open("small_file_to_overwrite.txt", "w") as f:
			f.write("y" * 10)

		with self.fs.open("large_file_to_overwrite.bin", "wb") as f:
			f.write(b"x" * 4000000)

		with self.fs.open("large_file_to_overwrite.bin", "wb") as f:
			f.write(b"y" * 4000000)

		with self.fs.open("large_file_to_overwrite.txt", "w") as f:
			f.write("x" * 4000000)

		with self.fs.open("large_file_to_overwrite.txt", "w") as f:
			f.write("y" * 4000000)


	def test_photo_metadata(self):
		with self.fs.open("canon-ixus.jpg", "wb") as target:
			with open("tests/canon-ixus.jpg", "rb") as source:
				target.write(source.read())

		# sometimes it take a few seconds for the server to process EXIF data
		# until it's processed, the "photo" section should be missing
		for i in range(3):
			info_ = self.fs.getinfo("canon-ixus.jpg")

			self.assertTrue(info_.get("photo", "camera_make") in [None, "Canon"])
			self.assertTrue(info_.get("photo", "camera_model") in [None, "Canon DIGITAL IXUS"])
			self.assertTrue(info_.get("photo", "exposure_denominator") in [None, 350])
			self.assertTrue(info_.get("photo", "exposure_numerator") in [None, 1])
			self.assertTrue(info_.get("photo", "focal_length") in [None, 10.8125])
			self.assertTrue(info_.get("photo", "f_number") in [None, 4.0])
			self.assertTrue(info_.get("photo", "taken_date_time") in [None, datetime(2001, 6, 9, 15, 17, 32)])
			self.assertTrue(info_.get("photo", "iso") in [None])
			self.assertTrue(info_.get("image", "width") in [None, 640])
			self.assertTrue(info_.get("image", "height") in [None, 480])
			if info_.get("photo", "camera_make") is not None:
				break
			sleep(5)
		else:
			self.assertTrue(False, "EXIF metadata not processed in 10s")

	def test_photo_metadata2(self):
		with self.fs.open("DSCN0010.jpg", "wb") as target:
			with open("tests/DSCN0010.jpg", "rb") as source:
				target.write(source.read())

		# sometimes it take a few seconds for the server to process EXIF data
		# until it's processed, the "photo" section should be missing
		for i in range(3):
			info_ = self.fs.getinfo("DSCN0010.jpg")

			self.assertTrue(info_.get("photo", "camera_make") in [None, "NIKON"])
			self.assertTrue(info_.get("photo", "camera_model") in [None, "COOLPIX P6000"])
			self.assertTrue(info_.get("photo", "exposure_denominator") in [None, 300.0])
			self.assertTrue(info_.get("photo", "exposure_numerator") in [None, 4.0])
			self.assertTrue(info_.get("photo", "focal_length") in [None, 24.0])
			self.assertTrue(info_.get("photo", "f_number") in [None, 5.9])
			self.assertTrue(info_.get("photo", "taken_date_time") in [None, datetime(2008, 10, 22, 16, 28, 39)])
			self.assertTrue(info_.get("photo", "iso") in [None, 64])
			self.assertTrue(info_.get("image", "width") in [None, 640])
			self.assertTrue(info_.get("image", "height") in [None, 480])
			self.assertTrue(info_.get("location", "latitude") in [None, 43.46744833333334])
			self.assertTrue(info_.get("location", "longitude") in [None, 11.885126666663888])
			if info_.get("photo", "camera_make") is not None:
				break
			sleep(5)
		else:
			self.assertTrue(False, "EXIF metadata not processed in 10s")

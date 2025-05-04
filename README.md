# GDriveFileManager
Python implementation of a Google Drive File Manager that allows to create, update and delete files in Google Drive

***NOTE: it requires to create an configure a proper service account from Google Cloud in order to allow GDrive File Manager to be able to manipulate files into Google Drive.***
***The service account MUST be given the proper permissions to the Google Drive folders/files to be able to access them***

## Limitations
### Drive selection
Current implementation does not allow to select the drive to work into.
The Google Drive File Manager methods simply assume that the service account only has access to files it could manipulate without compromising files it should not access to, regardless of the target drive

### File Search
The current implementation comes with a **heavy limitation** related to file search.
Google Drive allows multiple files to be stored with the same name, even if they are stored in the same folder.

The Google Drive API that perform file search based on the filename will return a list of all the files with the given filename the used service account has access to.

This means that when the user calls methods to update and/or delete a file, the current implementation of the Google Drive File Manager will select a ***RANDOM*** entry.

#### Example
Method *deleteFile* will accept a filename as an argument. If multiple files have the same name, a random one is selected and deleted from Google Drive
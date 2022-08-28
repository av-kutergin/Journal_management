# photo_booth

Django project for storing and managing data.
The project consists of 2 parts: one part is for everyone to see and another is for managers to upload new data. Django.admin is customized for the needs of the project.

## Quick start
- Clone the project from GitHub to your machine
- Install dependencies from requirements.txt
- Navigate to the 'photo_booth' directory and run command `manage.py migrate` to creade database
- To start your localhost server run command `manage.py runserver` in the terminal from 'photo_booth' directory

## API/Route Table
| Route                                        | Description                                                                                     |
|----------------------------------------------|-------------------------------------------------------------------------------------------------|
| /                                            | Main page, list of all cities                                                                   |
| /registry/:city_code                         | List of all journals in the selected city                                                       |
| /registry/:city_code/:journal_name           | List of all photos in the selected journal                                                      |
| /registry/:city_code/:journal_name/:photo_id | Selected photo image                                                                            |
| /manage                                      | Managers page (for logged in users redirects to /manage/cities else redirects to /manage/login) |
| /manage/login                                | Login page                                                                                      |
| /manage/cities                               | Displays he list of available cities for current user                                           |
| /manage/cities/:city_code                    | Information about journals in the city with an upload form for new photo                        |

## Technologies
Project is created with:
- Django version 4.1
- Pillow version 9.2.0
- HTML 5
- CSS

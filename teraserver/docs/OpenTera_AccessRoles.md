 # OpenTera Service access roles
 
 This table shows the various features that are available according the user groups access level, and for super admin access.
 
 ## User API
| Feature  [1]              | Super Admin                                                  | Site Role: *Admin* [2]                                          | Site Role: *User* [3]                                         | Project Role: *Admin* [4]                                     | Project Role: *User* 
| :---                   | :---:                                                        | :---: | :---: | :---: | :---: 
| **System Services**        | ![False](https://via.placeholder.com/15/ff0000/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+)
| **System Service: Logger**: Read      | ![ True](https://via.placeholder.com/15/00ff00/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+)
| **Services**: Read         | ![ True](https://via.placeholder.com/15/00ff00/000000?text=+) | ![True](https://via.placeholder.com/15/00ff00/000000?text=+)   | ![ True](https://via.placeholder.com/15/00ff00/000000?text=+) | ![True](https://via.placeholder.com/15/00ff00/000000?text=+) | ![True](https://via.placeholder.com/15/00ff00/000000?text=+)
| **Services**: Create / Update / Delete       | ![T rue](https://via.placeholder.com/15/00ff00/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+)
| **Sites**: Create          | ![ True](https://via.placeholder.com/15/00ff00/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+)
| **Sites**: Read       | ![ True](https://via.placeholder.com/15/00ff00/000000?text=+) | ![True](https://via.placeholder.com/15/00ff00/000000?text=+) | ![ True](https://via.placeholder.com/15/00ff00/000000?text=+) | ![ True](https://via.placeholder.com/15/00ff00/000000?text=+) | ![ True](https://via.placeholder.com/15/00ff00/000000?text=+)
| **Sites**: Update       | ![ True](https://via.placeholder.com/15/00ff00/000000?text=+) | ![ True](https://via.placeholder.com/15/00ff00/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+)
| **Sites**: Delete          | ![ True](https://via.placeholder.com/15/00ff00/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+) 
| **Projects**: Create  | ![ True](https://via.placeholder.com/15/00ff00/000000?text=+) | ![ True](https://via.placeholder.com/15/00ff00/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+)
| **Projects**: Read       | ![ True](https://via.placeholder.com/15/00ff00/000000?text=+) | ![True](https://via.placeholder.com/15/00ff00/000000?text=+) | ![ True](https://via.placeholder.com/15/00ff00/000000?text=+) | ![ True](https://via.placeholder.com/15/00ff00/000000?text=+) | ![ True](https://via.placeholder.com/15/00ff00/000000?text=+)
| **Projects**: Update       | ![ True](https://via.placeholder.com/15/00ff00/000000?text=+) | ![ True](https://via.placeholder.com/15/00ff00/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+) | ![ True](https://via.placeholder.com/15/00ff00/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+)
| **Projects**: Delete  | ![ True](https://via.placeholder.com/15/00ff00/000000?text=+) | ![ True](https://via.placeholder.com/15/00ff00/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+) | ![False](https://via.placeholder.com/15/ff0000/000000?text=+)

[1] All features are filtered according to the specific user group access. For exemple, if **Sites: Read** is done, only sites where the user have access with its usergroups are read.

[2] Super admins always have a **Site Role: Admin** on all sites in the system

[3] Any user group with a role in a project automatically have a **Site Role: User** access

[4] Any user group with a **Site Role: Admin** automatically have a **Project Role: Admin**
 ## Project level features

from .structs import ErrorMessage


UNKNOWN_ERROR_CODE = 5000
PARSE_ERROR_CODE = 1000

RESTRICTION_VIOLATION_ERROR_CODE = 500
DATA_INTEGRITY_ERROR_CODE = 501
OOO_ILLEGAL_PLACE_ERROR_CODE = 502

COULD_NOT_OPTIMIZE_ERROR = ErrorMessage(100, 'The problem could not be solved.')
WRONG_EXCEL_FORMAT_ERROR = ErrorMessage(101, 'The format of excel file is not right.')
WRONG_FILE_FORMAT_ERROR = ErrorMessage(102, 'The file provided has not excel format.')
NO_FILE_ERROR = ErrorMessage(103, 'No file was provided.')
ALREADY_INITED_ERROR = ErrorMessage(104, 'The layout is already initialized.')
NO_ROWS_REQUESTED_ERROR = ErrorMessage(105, 'The init file does not contain rows with airports provided with layout name.')
LAYOUT_DATES_NOT_EQUAL_ERROR = ErrorMessage(106, 'The dates in layout provided are not consistent with the dates of the previous layout.')

ILLEGAL_EDIT_TOKEN_ERROR = ErrorMessage(200, 'Illegal edit token has been provided.')
LAYOUT_ALREADY_EDITED_ERROR = ErrorMessage(201, 'The layout is being edited by another user.')
NO_EDIT_TOKEN_ERROR = ErrorMessage(202, 'Edit token was not provided.')
ILLEGAL_EDIT_MODE_OFF_ERROR = ErrorMessage(203, 'Illegal edit token provided to switch off edit mode.')

LAYOUT_NAME_FORMAT_ERROR = ErrorMessage(300, 'Layout name has wrong format.')

INVALID_CREDENTIALS_ERROR = ErrorMessage(400, 'Wrong username or password.')

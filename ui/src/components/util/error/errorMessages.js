const codes = {
  COULD_NOT_OPTIMIZE: 100,
  WRONG_EXCEL_FORMAT: 101,
  WRONG_FILE_FORMAT: 102,
  NO_FILE: 103,
  ALREADY_INITED: 104,
  LAYOUT_NAME_FORMAT_ERROR: 105,
  LAYOUT_DATES_NOT_EQUAL_ERROR: 106,

  ILLEGAL_EDIT_TOKEN: 200,
  LAYOUT_ALREADY_EDITED: 201,
  NO_EDIT_TOKEN: 202,
  ILLEGAL_EDIT_MODE_ERROR: 203,

  INVALID_CREDENTIALS_ERROR: 400,

  RESTRICTION_VIOLATION: 500,
  DATA_INTEGRITY: 501,
  OOO_ILLEGAL_PLACE: 502,

  PARSE_ERROR: 1000,
  UNKNOWN_ERROR: 5000,
};

const messages = {
  [codes.COULD_NOT_OPTIMIZE]: 'Невозможно завершить расчет данных раскладки. Измените параметры и попробуйте еще раз.',
  [codes.WRONG_EXCEL_FORMAT]: 'Неверный формат excel-файла.',
  [codes.WRONG_FILE_FORMAT]: 'Выбранный файл не является файлом excel.',
  [codes.NO_FILE]: 'Файл не был выбран.',
  [codes.ALREADY_INITED]: 'Раскладка уже была создана.',
  [codes.LAYOUT_NAME_FORMAT_ERROR]: 'Файл не содержит данные с названием аэропорта, указанном при создании раскладки.',
  [codes.LAYOUT_DATES_NOT_EQUAL_ERROR]: 'Даты в выбранном файле не совпадают с датами обновляемой раскладки.',

  [codes.ILLEGAL_EDIT_TOKEN]: 'Ваша сессия устарела. Обновите страницу.',
  [codes.LAYOUT_ALREADY_EDITED]: 'В данный момент раскладка редактируется другим пользователем. Подождите некоторое время.',
  [codes.NO_EDIT_TOKEN]: 'Вы не можете редактировать раскладку, так как не вошли в режим редактирования.',
  [codes.ILLEGAL_EDIT_MODE_ERROR]: 'Выход из режима редактирования был завершен неудачно.',

  [codes.INVALID_CREDENTIALS_ERROR]: 'Неправильные логин и/или пароль.',

  [codes.RESTRICTION_VIOLATION]: 'Нарушено одно из ограничений на максимальное количество мест.',
  [codes.DATA_INTEGRITY]: 'Данные о раскладке не совпадают с данными на сервере.',
  [codes.OOO_ILLEGAL_PLACE]: 'Одно или несколько значений в ячейках нестандартных длительностей расположено неверно.',

  [codes.PARSE_ERROR]: 'Возможно, используется устраевшая версия. Обратитесь к администратору приложения.',
  [codes.UNKNOWN_ERROR]: 'Что-то пошло не так. Обратитесь к администратору приложения.',
};

const buildUIError = message => ({ status: 400, data: { message } });

export default {
  codes, messages, buildUIError
};

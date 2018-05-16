import sum from 'lodash/sum';
import { checkInt } from '../../util/validations';
import {
  MUST_BE_A_NUMBER_LABEL,
  DESCRIPTION_ENTER_PRIORITIES,
  REQUIRED_FIELD_LABEL
} from '../../../constants/constants';

const validate = (values) => {
  const errors = {
    priorities: []
  };

  const { priorities } = values;
  if (priorities && priorities.length) {
    priorities.forEach((priority, index) => {
      if (!priority) {
        errors.priorities[index] = REQUIRED_FIELD_LABEL;
      }
      if (!checkInt(priority)) {
        errors.priorities[index] = MUST_BE_A_NUMBER_LABEL;
      }
    });

    const prioritiesInt = priorities.map(item => Number(item));
    if (sum(prioritiesInt) !== 100) {
      const lastPriorityIndex = priorities.length - 1;
      errors.priorities[lastPriorityIndex] = DESCRIPTION_ENTER_PRIORITIES;
    }
  }

  return errors;
};

export default validate;

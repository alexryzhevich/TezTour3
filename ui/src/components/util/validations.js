import isInteger from 'lodash/isInteger';
import {
  MUST_BE_A_NUMBER_LABEL,
  REQUIRED_FIELD_LABEL,
  MUST_BE_LESS_LABEL,
  MUST_BE_MORE_LABEL,
} from '../../constants/constants';

export const checkInt = (value) => {
  if (typeof value === 'number') {
    return isInteger(value);
  }
  if (typeof value === 'string') {
    return /^(0|[1-9]\d*)$/.test(value);
  }
  return false;
};

export const integer = value => (checkInt(value)
  ? undefined
  : MUST_BE_A_NUMBER_LABEL);

export const required = value => (value
  ? undefined
  : REQUIRED_FIELD_LABEL);

export const maxValue = max => value => (value > max
  ? `${MUST_BE_LESS_LABEL} ${max}`
  : undefined);

export const minValue = min => value => (value < min
  ? `${MUST_BE_MORE_LABEL} ${min}`
  : undefined);

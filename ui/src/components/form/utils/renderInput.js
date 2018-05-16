import React from 'react';
import { Input } from 'reactstrap';

const renderInput = ({
  input, label, meta: { touched, error }, ...custom
}) => {
  const props = {
    placeholder: label,
    ...(touched && error) && {
      valid: false
    },
    ...input,
    ...custom
  };

  return <Input {...props} />;
};

export default renderInput;

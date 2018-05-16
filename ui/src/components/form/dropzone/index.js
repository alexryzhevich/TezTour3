import React from 'react';
import Dropzone from 'react-dropzone';
import './Dropzone.css';
import {
  ILLEGAL_FILE_FORMAT_LABEL,
  DROP_FILE_LABEL,
  CHOOSE_FILE_LABEL
} from '../../../constants/constants';

const EXCEL_FORMATS = 'application/vnd.ms-excel, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';


const FileDropzone = ({ onDrop, accepted, rejected }) => {
  let className = 'Dropzone';
  if (accepted.length) {
    className = 'Dropzone success';
  }
  if (rejected.length) {
    className = 'Dropzone error';
  }

  const props = {
    accept: EXCEL_FORMATS,
    onDrop,
    multiple: false,
    className
  };

  return (
    <Dropzone {...props}>
      {
          rejected.length === 0
            ? (
              <p>
                <strong>{CHOOSE_FILE_LABEL}</strong>{DROP_FILE_LABEL}
              </p>
            )
            : <p>{ILLEGAL_FILE_FORMAT_LABEL}</p>
        }
    </Dropzone>
  );
};

export default FileDropzone;

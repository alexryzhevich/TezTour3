import React from 'react';
import { CardBody, Row, Col, Button } from 'reactstrap';
import { EDIT_BUTTON_TITLE } from '../../../constants/constants';
import LayoutName from './LayoutName';

class ClosedBody extends React.PureComponent {
  render() {
    const { layoutName, openEditMode, updateFromFileDate } = this.props;

    return (
      <CardBody>
        <Row>
          <Col
            md={3}
            className="toolbar-panel left"
          >
            <Button color="primary" onClick={openEditMode}>{ EDIT_BUTTON_TITLE }</Button>
          </Col>
          <Col md={6}>
            <LayoutName layoutName={layoutName} updateFromFileDate={updateFromFileDate} />
          </Col>
          <Col md={3} />
        </Row>
      </CardBody>
    );
  }
}

export default ClosedBody;

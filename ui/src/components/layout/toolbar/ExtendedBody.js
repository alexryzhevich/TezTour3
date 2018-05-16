import React from 'react';
import { CardBody, Row, Col } from 'reactstrap';
import CommonActions from './CommonActions';
import EditPrioritiesMode from './EditPrioritiesMode';
import EditMode from './edit-mode';
import LayoutName from './LayoutName';

class ExtendedBody extends React.PureComponent {
  render() {
    const {
      isEditPrioritiesModeEnabled, layoutName, updateFromFileDate, ...actions
    } = this.props;

    return (
      <CardBody>
        <Row>
          <Col
            md={4}
            className="toolbar-panel left"
          >
            <CommonActions {...actions} />
          </Col>
          <Col md={4}>
            <LayoutName layoutName={layoutName} updateFromFileDate={updateFromFileDate} />
          </Col>
          <Col
            md={4}
            className="toolbar-panel right"
          >
            {
              isEditPrioritiesModeEnabled
                ? <EditPrioritiesMode />
                : <EditMode />
            }
          </Col>
        </Row>
      </CardBody>
    );
  }
}

export default ExtendedBody;

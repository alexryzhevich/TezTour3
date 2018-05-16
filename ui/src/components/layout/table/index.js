import React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import ReactTable from 'react-table';
import checkboxHOC from 'react-table/lib/hoc/selectTable';
import { toggleSelection } from '../../../actions/data';
import './Table.css';

const CheckboxTable = checkboxHOC(ReactTable);

class LayoutTable extends React.Component {
  constructor(props) {
    super(props);

    this.isSelected = this.isSelected.bind(this);
  }

  isSelected(key) {
    return this.props.selectedDates.includes(key);
  }

  render() {
    const {
      isSelectable, data, columns, toggleSelection
    } = this.props;

    const props = {
      data,
      columns,
      showPagination: false,
      sortable: false,
      resizable: false,
      defaultPageSize: data.length,
      className: 'layout-table -highlight'
    };

    if (!isSelectable) {
      return <ReactTable {...props} />;
    }

    const checkboxProps = {
      toggleSelection,
      isSelected: this.isSelected,
      selectType: 'checkbox',
    };

    return <CheckboxTable {...props} {...checkboxProps} />;
  }
}

LayoutTable.defaultProps = {
  isSelectable: false
};

const mapStateToProps = state => ({
  selectedDates: state.layout.data.selectedDates
});

const mapDispatchToProps = dispatch => bindActionCreators({ toggleSelection }, dispatch);

export default connect(mapStateToProps, mapDispatchToProps)(LayoutTable);

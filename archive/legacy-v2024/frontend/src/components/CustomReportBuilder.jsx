import React, { useState } from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import './CustomReportBuilder.css';

// Sample available analytics fields
const availableFields = [
  { id: 'field-1', name: 'Page Views' },
  { id: 'field-2', name: 'Unique Visitors' },
  { id: 'field-3', name: 'Bounce Rate' },
  { id: 'field-4', name: 'Session Duration' },
  { id: 'field-5', name: 'Conversion Rate' },
];

function CustomReportBuilder() {
  const [fields, setFields] = useState(availableFields);
  const [reportFields, setReportFields] = useState([]);

  // Handles drag end event
  const onDragEnd = (result) => {
    const { source, destination } = result;

    // dropped outside a droppable area
    if (!destination) {
      return;
    }

    // Dragging from available fields to report builder
    if (source.droppableId === 'availableFields' && destination.droppableId === 'reportFields') {
      const movedField = fields[source.index];
      // Prevent duplicates
      if (reportFields.find(f => f.id === movedField.id)) {
        return;
      }
      const newReportFields = Array.from(reportFields);
      newReportFields.splice(destination.index, 0, movedField);
      setReportFields(newReportFields);
      return;
    }

    // Rearranging inside reportFields
    if (source.droppableId === 'reportFields' && destination.droppableId === 'reportFields') {
      const newReportFields = Array.from(reportFields);
      const [moved] = newReportFields.splice(source.index, 1);
      newReportFields.splice(destination.index, 0, moved);
      setReportFields(newReportFields);
      return;
    }

    // Removing field from report builder
    if (source.droppableId === 'reportFields' && destination.droppableId === 'availableFields') {
      // Remove from reportFields
      const newReportFields = Array.from(reportFields);
      newReportFields.splice(source.index, 1);
      setReportFields(newReportFields);
      return;
    }
  };

  const handleSaveReport = () => {
    // For demo, just alert JSON of selected fields
    alert('Report Fields: ' + JSON.stringify(reportFields.map(f => f.name)));
    // In real app, send to backend API
  };

  return (
    <div className="custom-report-builder">
      <h2>Custom Report Builder</h2>
      <div className="drag-drop-container">
        <DragDropContext onDragEnd={onDragEnd}>
          <div className="fields-list">
            <h3>Available Fields</h3>
            <Droppable droppableId="availableFields" isDropDisabled={false}>
              {(provided) => (
                <div
                  className="droppable-area"
                  {...provided.droppableProps}
                  ref={provided.innerRef}
                >
                  {fields.map((field, index) => (
                    <Draggable key={field.id} draggableId={field.id} index={index}>
                      {(provided, snapshot) => (
                        <div
                          className={`field-item ${snapshot.isDragging ? 'dragging' : ''}`}
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                        >
                          {field.name}
                        </div>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </div>

          <div className="fields-list">
            <h3>Report Fields</h3>
            <Droppable droppableId="reportFields">
              {(provided) => (
                <div
                  className="droppable-area report-fields"
                  {...provided.droppableProps}
                  ref={provided.innerRef}
                >
                  {reportFields.length === 0 && <div className="empty-placeholder">Drag fields here to build report</div>}
                  {reportFields.map((field, index) => (
                    <Draggable key={field.id} draggableId={field.id} index={index}>
                      {(provided, snapshot) => (
                        <div
                          className={`field-item ${snapshot.isDragging ? 'dragging' : ''}`}
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                        >
                          {field.name}
                        </div>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </div>
        </DragDropContext>
      </div>
      <button className="save-button" onClick={handleSaveReport} disabled={reportFields.length === 0}>
        Save Report
      </button>
    </div>
  );
}

export default CustomReportBuilder;

interface ConfirmDialogProps {
  text: string;
  yesLabel: string;
  noLabel: string;
  onYes: () => void;
  onNo: () => void;
}

// Asks once before an action that cannot be taken back. Choosing "no" sends
// nothing.
export default function ConfirmDialog(props: ConfirmDialogProps) {
  return (
    <div role="alertdialog" aria-modal="true" className="sh-confirm">
      <p className="sh-confirm-text">{props.text}</p>
      <button type="button" className="sh-button" onClick={props.onYes}>
        {props.yesLabel}
      </button>
      <button
        type="button"
        className="sh-button sh-button-quiet"
        onClick={props.onNo}
      >
        {props.noLabel}
      </button>
    </div>
  );
}

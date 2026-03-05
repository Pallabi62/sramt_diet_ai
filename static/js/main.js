
// main.js - WebSocket (Socket.IO) integration for real-time card moves
// Assumes cards have data-card-id, lists have data-list-id, and board has data-board-id.
// Also assumes existing drag/drop logic calls onCardDrop(cardEl, destListEl, destIndex).

// Connect to Socket.IO server (served from same host)
const socket = io(); // requires <script src="/socket.io/socket.io.js"></script> in HTML

// Join board room after connecting (so server can broadcast only to same board)
const boardEl = document.querySelector('[data-board-id]');
const BOARD_ID = boardEl ? boardEl.dataset.boardId : null;
socket.on('connect', () => {
  if (BOARD_ID) socket.emit('join_board', { board_id: BOARD_ID });
});

// Emit when this client moves a card locally
function emitCardMoved(cardId, newListId, newPosition) {
  const payload = {
    card_id: cardId,
    list_id: newListId,
    position: newPosition,
    board_id: BOARD_ID,
    client_id: socket.id
  };
  socket.emit('card_moved', payload);
}

// Listen for card_moved from server and update DOM (but ignore our own emits)
socket.on('card_moved', (data) => {
  try {
    if (!data || data.client_id === socket.id) return; // ignore if originated from this client

    const { card_id, list_id, position } = data;
    const cardEl = document.querySelector(`[data-card-id="${card_id}"]`);
    const destList = document.querySelector(`[data-list-id="${list_id}"]`);
    if (!cardEl || !destList) return;

    // Remove card from current parent
    cardEl.remove();

    // Insert at specified position (0-based). If position is out of range, append.
    const children = Array.from(destList.querySelectorAll('.card'));
    if (position >= 0 && position < children.length) {
      destList.insertBefore(cardEl, children[position]);
    } else {
      destList.appendChild(cardEl);
    }
  } catch (err) {
    console.error("Error processing incoming card_moved:", err);
  }
});

// Example hook into existing drag/drop logic -- adapt to your code
function onCardDrop(cardEl, destListEl, destIndex) {
  // Update local DOM already done by your drag/drop handler; then emit to server:
  const cardId = cardEl.dataset.cardId;
  const newListId = destListEl.dataset.listId;
  const newPosition = destIndex;
  emitCardMoved(cardId, newListId, newPosition);
}

// Optional: handle card updates when server broadcasts confirmations
socket.on('card_update_confirm', (data) => {
  // handle ack if needed
});

  // ----- Login checkbox 檢查 -----
  const loginForm = document.getElementById("login-form");
  const agreeCheckbox = document.getElementById("agree-checkbox");

  // addEventListener 用來監聽使用者行為（事件 event），像是 click、submit、input 等
  // 監聽後會觸發一個回呼函式
  if (loginForm && agreeCheckbox) {
    loginForm.addEventListener("submit", (event) => {
      if (!agreeCheckbox.checked) {
        event.preventDefault();
        alert("請勾選同意條款");
      }
    });
  }
 
  // ----- Hotel ID 檢查與導向 -----
  const hotelIdInput = document.getElementById("hotel-id-input");
  const hotelSearchButton = document.getElementById("hotel-search-btn");

  if (hotelIdInput && hotelSearchButton) {
  hotelSearchButton.addEventListener("click", () => {
    const value = hotelIdInput.value.trim();

    // 字串模式比對 / ... / 包住的是規則，.test(value) 會回傳布林值（true/false）
    // ! 代表取反｜^ → 開頭｜[1-9] → 第一個數字必須是 1–9｜\d* → 後面可以接 0 個或多個數字｜$ → 結尾
    // ⇒ 代表「正整數」（不能是 0 或小數）
    if (!/^[1-9]\d*$/.test(value)) {
      // 非正整數時：alert「請輸入正整數」+ return（中斷，不繼續執行）；是正整數時跳過 if 區塊，繼續往下執行
      alert("請輸入正整數");
      return;
    }
    // 頁面導向，導向 /hotel/輸入值 這個頁面
    window.location.href = `/hotel/${value}`;
  });
}

const tg = window.Telegram.WebApp;
tg.expand();
tg.ready();

const SUBCATEGORIES = {
  "Хендимен": [
    "Мелкий ремонт по дому",
    "Сборка мебели",
    "Электрика / сантехника (мелкая)",
    "Другое",
  ],
  "Техника и ПК": [
    "Диагностика, чистка, удаление вирусов",
    "Переустановка системы",
    "Замена компонентов",
    "Настройка Wi-Fi / роутера",
    "Принтер / умный дом",
    "Перенос данных на новое устройство",
    "Другое",
  ],
  "Сайты и боты": [
    "Лендинг",
    "Интернет-магазин",
    "Сайт-визитка",
    "Telegram-бот (запись / заказы / рассылки)",
    "Автоматизация задач",
    "Другое",
  ],
};

const state = {
  category: null,
  subcategory: null,
  format: null,
};

const categoryGroup = document.getElementById("category-group");
const formatGroup = document.getElementById("format-group");
const subcategoryField = document.getElementById("subcategory-field");
const subcategorySelect = document.getElementById("subcategory");
const addressField = document.getElementById("address-field");
const descriptionInput = document.getElementById("description");
const errorText = document.getElementById("error-text");

function selectChip(group, button, onSelect) {
  [...group.children].forEach((chip) => chip.classList.remove("selected"));
  button.classList.add("selected");
  onSelect(button.dataset.value);
}

categoryGroup.addEventListener("click", (e) => {
  const button = e.target.closest(".chip");
  if (!button) return;
  selectChip(categoryGroup, button, (value) => {
    state.category = value;
    subcategorySelect.innerHTML = "";
    SUBCATEGORIES[value].forEach((option) => {
      const opt = document.createElement("option");
      opt.value = option;
      opt.textContent = option;
      subcategorySelect.appendChild(opt);
    });
    state.subcategory = SUBCATEGORIES[value][0];
    subcategoryField.hidden = false;
  });
  validate();
});

subcategorySelect.addEventListener("change", (e) => {
  state.subcategory = e.target.value;
});

formatGroup.addEventListener("click", (e) => {
  const button = e.target.closest(".chip");
  if (!button) return;
  selectChip(formatGroup, button, (value) => {
    state.format = value;
    addressField.hidden = value !== "Выезд";
  });
  validate();
});

descriptionInput.addEventListener("input", validate);

function validate() {
  const valid = Boolean(state.category && descriptionInput.value.trim().length >= 5);
  if (valid) {
    tg.MainButton.enable();
  } else {
    tg.MainButton.disable();
  }
  return valid;
}

function showError(message) {
  errorText.textContent = message;
  errorText.hidden = false;
}

function hideError() {
  errorText.hidden = true;
}

async function submitOrder() {
  hideError();
  if (!validate()) return;

  tg.MainButton.showProgress();

  const payload = {
    initData: tg.initData,
    category: state.category,
    subcategory: state.subcategory,
    description: descriptionInput.value.trim(),
    contact_phone: document.getElementById("contact_phone").value.trim() || null,
    address: document.getElementById("address").value.trim() || null,
    format: state.format,
  };

  try {
    const response = await fetch("/api/order", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error("request_failed");
    }

    tg.MainButton.hideProgress();
    tg.showPopup(
      {
        title: "Готово!",
        message: "Заявка отправлена, я скоро с вами свяжусь.",
        buttons: [{ type: "ok" }],
      },
      () => tg.close()
    );
  } catch (err) {
    tg.MainButton.hideProgress();
    showError("Не удалось отправить заявку. Проверьте соединение и попробуйте ещё раз.");
  }
}

tg.MainButton.setText("Отправить заявку");
tg.MainButton.disable();
tg.MainButton.show();
tg.MainButton.onClick(submitOrder);

tg.expand();

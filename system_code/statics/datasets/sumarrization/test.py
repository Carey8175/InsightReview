from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from datasets import load_dataset
from peft import LoraConfig, get_peft_model

# 模型名称，替换为你实际使用的模型名称或本地路径
model_name = "qwen2.53B"
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", trust_remote_code=True)

# 设置 LoRA 配置（参数可根据需要调节）
lora_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],  # 根据模型结构可能需要调整
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM"
)

# 为模型附加 LoRA 层
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()  # 查看可训练参数

# 加载预处理后的数据集
dataset = load_dataset('json', data_files='processed.jsonl', split='train')

# 格式化数据，将 instruction 和 input 拼接为模型输入，目标为 output（标题）
def format_prompt(example):
    # 拼接提示语和文章内容
    prompt = example["instruction"] + "\n" + example["input"]
    example["prompt"] = prompt
    # 目标文本为标题
    example["target"] = example["output"]
    return example

dataset = dataset.map(format_prompt)

# 定义 tokenize 函数，将 prompt 与目标文本拼接后进行编码
def tokenize_function(example):
    texts = [instr + "\n" + target for instr, target in zip(example["prompt"], example["target"])]
    tokenized = tokenizer(texts, truncation=True, max_length=512)
    return tokenized

tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=dataset.column_names)

# 定义训练参数
training_args = TrainingArguments(
    output_dir="./qwen2.53B-lora-sft",
    per_device_train_batch_size=2,    # 根据显存调整 batch size
    num_train_epochs=3,               # 根据数据量调整 epoch 数
    logging_steps=10,
    save_steps=50,
    learning_rate=2e-4,
    fp16=True,
    report_to="none"
)

data_collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=data_collator,
)

# 开始微调
trainer.train()
# 保存微调后的模型
model.save_pretrained("./qwen2.53B-lora-sft-final")

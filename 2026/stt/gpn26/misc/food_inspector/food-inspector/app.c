#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BUFFER_SIZE 0x80
char name[BUFFER_SIZE];
char choice[BUFFER_SIZE];

typedef enum
{
    SIMPLE,
    CHOICES,
} dialog_type;

#define NUM_CHOICES 3
struct dialog;
typedef struct
{
    char *name;
    struct dialog *dialog;
} choice_option;

typedef struct
{
    char *start_text;
    char *continuation_text;
    choice_option options[NUM_CHOICES];
} choice_data;

typedef struct dialog
{
    dialog_type type;
    struct dialog *next;
    union data
    {
        char *text;
        choice_data choices;
    } data;
} dialog;

// Dialogs
dialog DIALOG_MAIN;
dialog DIALOG_END;
dialog DIALOG_BAR;
dialog DIALOG_BAR_1;
dialog DIALOG_BAR_2;
dialog DIALOG_BAR_3;
dialog DIALOG_KITCHEN;
dialog DIALOG_KITCHEN_1;
dialog DIALOG_KITCHEN_2;
dialog DIALOG_KITCHEN_3;
dialog DIALOG_STOREROOM;
dialog DIALOG_STOREROOM_1;
dialog DIALOG_STOREROOM_2;
dialog DIALOG_STOREROOM_3;

dialog DIALOG_START = {
    SIMPLE,
    &DIALOG_MAIN,
    "[Waiter] Of course, let me get the manager for you.\n"
    "The waiter moves to the kitchen door and calls out.\n"
    "[Waiter] Luigi, %1$s from the health department has come to perform a routine inspection of our restaurant. Can you please come?\n"
    "[Luigi (muffled)] Si, give me a moment.\n"
    "Meanwhile, you visit the restroom and wash your hands. As you come back, Luigi leaves the kitchen and welcomes you.\n"};
dialog DIALOG_MAIN = {
    CHOICES,
    &DIALOG_END,
    {
        .choices = {"[Luigi] Buon giorno %1$s, I am Luigi, the manager of this pizzeria. Where would you like to start your inspection?\n",
                    "[Luigi] Where would you like to continue your inspection?\n",
                    {{"The bar", &DIALOG_BAR}, {"The kitchen", &DIALOG_KITCHEN}, {"The storeroom", &DIALOG_STOREROOM}}},
    }};
dialog DIALOG_BAR = {
    CHOICES,
    NULL,
    {
        .choices = {"You enter the bar at the front of the house.\n"
                    "[Luigi] This is our bar where we prepare drinks, handle dishes and hand over food to our waiters.\n"
                    "What do you inspect first?\n",
                    "What do you inspect next?\n",
                    {{"Drinks", &DIALOG_BAR_1}, {"Dishes", &DIALOG_BAR_2}, {"Menus", &DIALOG_BAR_3}}},
    }};
dialog DIALOG_BAR_1 = {
    SIMPLE,
    NULL,
    "The drinks are well-ordered behind the counter and the restaurant has a coffee machine that is clean and well-kept despite its regular use.\n"
    "No red flags so far.\n"};
dialog DIALOG_BAR_2 = {
    SIMPLE,
    NULL,
    "[You] Where do you clean the dishes?\n"
    "[Luigi] Over here, at the back of the bar.\n"
    "He shows you a small scullery at one side of the bar. It features a commercial-grade dishwasher and a drying rack.\n"
    "A quick test shows that concentration of disinfectant is within the expected threshold and the dish detergent is appropriate for its use.\n"
    "Clean tableware is stored in cabinets behind the bar.\n"
    "No red flags so far.\n"};
dialog DIALOG_BAR_3 = {
    SIMPLE,
    NULL,
    "[You] May I take a look at the menu?\n"
    "[Luigi] Of course.\n"
    "You take a look at the menu that he hands you. All products and ingredients are clearly advertised and allergens are documented as well.\n"
    "No red flags so far.\n"};
dialog DIALOG_KITCHEN = {
    CHOICES,
    NULL,
    {
        .choices = {"You enter the kitchen together.\n"
                    "[Luigi] This is our pizza kitchen. Ingredients are prepared on this side of the kitchen and the pizzas are prepared next to our oven, right before baking.\n"
                    "What do you inspect first?\n",
                    "What do you inspect next?\n",
                    {{"Pizza oven", &DIALOG_KITCHEN_1}, {"Kitchen surfaces and ingredients", &DIALOG_KITCHEN_2}, {"Hygiene", &DIALOG_KITCHEN_3}}},
    }};
dialog DIALOG_KITCHEN_1 = {
    SIMPLE,
    NULL,
    "You check the service documentation and temperature of the oven. It is working well and is kept clean. The temperature is easily high enough to ensure that all ingredients are cooked well.\n"
    "No red flags so far.\n"};
dialog DIALOG_KITCHEN_2 = {
    SIMPLE,
    NULL,
    "All surfaces in the kitchen are clean. Pre-prepared ingredients are kept in closed boxes in a refrigerator.\n"
    "No red flags so far.\n"};
dialog DIALOG_KITCHEN_3 = {
    SIMPLE,
    NULL,
    "The chef and sous chefs are appropriate clothing and keep their hair inside hats and hair nets. While you watch, they regularly wash their hands with warm water at the back of the kitchen once they finish a preparation step.\n"
    "No red flags so far.\n"};
dialog DIALOG_STOREROOM = {
    CHOICES,
    NULL,
    {
        .choices = {"You enter the storeroom at the back of the kitchen.\n"
                    "[Luigi] This is our storeroom. Fresh ingredients are delivered in the morning and are stored in the fridge until they are used. The remaining ingredients are stored on the shelves over here. If you need anything, just ask me.\n"
                    "What do you inspect first?\n",
                    "What do you inspect next?\n",
                    {{"Refrigerator", &DIALOG_STOREROOM_1}, {"Storage shelves", &DIALOG_STOREROOM_2}, {"Delivery documentation", &DIALOG_STOREROOM_3}}},
    }};
dialog DIALOG_STOREROOM_1 = {
    SIMPLE,
    NULL,
    "You check the temperature logs on the fridge and test current temperature. The logs are well kept and the current temperature is within the acceptable threshold.\n"
    "Inside the fridge, products are clearly separated, labeled and ordered by delivery date.\n"
    "No red flags so far.\n"};
dialog DIALOG_STOREROOM_2 = {
    SIMPLE,
    NULL,
    "Inside the storage shelf, the various dry products are clearly labeled, closed containers. Everything looks well-organized and shows no sign of dirt or contamination.\n"
    "No red flags so far.\n"};
dialog DIALOG_STOREROOM_3 = {
    SIMPLE,
    NULL,
    "[You] Luigi, would please show me the delivery documentation?\n"
    "[Luigi] We use digital documentation everywhere. You can take a on here and I can also send you the full documentation later, if you like.\n"
    "He hands you a tablet with a folder of documents. The most current deliveries are from today and match the products in the storeroom. The suppliers are well-documented and match the register of the health department.\n"
    "No red flags so far.\n"
    "[You] Thanks, that will suffice for now. I will look at the remaining documentation in detail after the inspection.\n"};
dialog DIALOG_END = {
    SIMPLE,
    NULL,
    "[You] Thank you. I think, that concludes my inspection for now. You will receive a report with the results by mail soon, including the lab reports of the samples I took. I have no negative remarks so far, though.\n"
    "[Luigi] That is good to hear. Could you just send us the results via email, though?\n"
    "[You] Not yet, sadly. At least it's not by fax.\n"
    "[Luigi] Ah, yes, well... That's something, I guess. Have a nice day, %1$s, ciao!\n"
    "[You] You too, good bye!\n"
    "As you leave the restaurant, you keep wondering where they keep their flags...\n"};

void input(char *buffer, char *prompt)
{
    printf("%s> ", prompt);
    fgets(buffer, BUFFER_SIZE, stdin);
    buffer[strcspn(buffer, "\n")] = '\0';
}

const char *DONE = "done";
void run_dialog(dialog *this);
void run_choices(dialog *this)
{
    choice_data *data = &this->data.choices;
    bool first = true;

    while (true)
    {
        if (first)
        {
            printf(data->start_text, name);
            first = false;
        }
        else
        {
            printf(data->continuation_text, name);
        }
        for (int i = 0; i < NUM_CHOICES; i++)
        {
            printf("%d - %s\n", (i + 1), data->options[i].name);
        }
        printf("%s - Continue now\n", DONE);

        uint32_t selected = 0;
        while (true)
        {
            input(choice, "Choice");
            if (strcmp(choice, DONE) == 0)
            {
                return;
            }

            if (sscanf(choice, "%d", &selected) == 1 && --selected < NUM_CHOICES)
            {
                break;
            }
            puts("[ERROR] Invalid choice, try again");
        }

        run_dialog(data->options[selected].dialog);
    }
}

void run_dialog(dialog *this)
{
    switch (this->type)
    {
    case SIMPLE:
        printf(this->data.text, name);
        break;
    case CHOICES:
        run_choices(this);
        break;
    }

    if (this->next)
    {
        run_dialog(this->next);
    }
}

void init()
{
    setbuf(stdin, NULL);
    setbuf(stdout, NULL);
    setbuf(stderr, NULL);
}

int main()
{
    init();

    puts("You enter the pizzeria and are promptly greeted by a waiter.\n"
         "[Waiter] Welcome to Luigi's Pizzeria, how may I help you?\n"
         "[You] Good Morning, I'm ");
    input(name, "Name");
    puts("\tfrom the health department and I am here for a routine inspection of your restaurant.");
    run_dialog(&DIALOG_START);

    return EXIT_SUCCESS;
}